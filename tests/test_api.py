"""Unit tests for TerraPulse FastAPI Server & REST Endpoints."""

import pytest
from fastapi.testclient import TestClient
from terrapulse.api import app

client = TestClient(app)


def test_command_hud_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "TERRAPULSE" in response.text


def test_health_check_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "TerraPulse (CampTwin AI)"
    assert data["google_cloud_region"] == "asia-southeast1"


def test_digital_twin_endpoints():
    r_graph = client.get("/api/twin/graph")
    assert r_graph.status_code == 200
    data_g = r_graph.json()
    assert data_g["node_count"] > 20
    assert "assets" in data_g

    r_geo = client.get("/api/twin/geojson")
    assert r_geo.status_code == 200
    data_geo = r_geo.json()
    assert data_geo["type"] == "FeatureCollection"

    r_twi = client.get("/api/twin/twi")
    assert r_twi.status_code == 200
    assert "twi_indices" in r_twi.json()

    r_wash = client.get("/api/twin/wash-risk")
    assert r_wash.status_code == 200
    assert r_wash.json()["total_violations"] >= 1


def test_inspect_endpoint():
    payload = {
        "transcript": "Culvert C-14 has 75% silt blockage. Retaining wall BW-07 deflection 18.5 deg.",
        "asset_hint": "CULVERT_C14",
    }
    response = client.post("/api/inspect", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["defects_detected"]) >= 2
    assert data["risk_score"] > 0.5


def test_cascade_simulate_endpoint():
    payload = {
        "gpm_rain_rate_mm_hr": 65.0,
        "sentinel1_soil_saturation": 0.88,
        "copernicus_dem_slope_deg": 22.5,
    }
    response = client.post("/api/cascade/simulate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["cascade_probability"] > 0.8
    assert len(data["stages"]) == 5


def test_scenarios_and_benchmark_endpoints():
    r_sc = client.get("/api/scenarios")
    assert r_sc.status_code == 200
    scenarios = r_sc.json()
    assert len(scenarios) >= 4

    # Run scenario
    r_run = client.post("/api/scenarios/monsoon_65mm_camp4/run")
    assert r_run.status_code == 200
    data_run = r_run.json()
    assert data_run["scenario_id"] == "monsoon_65mm_camp4"
    assert "dispatch" in data_run

    # Benchmark endpoint
    r_bench = client.get("/api/benchmark")
    assert r_bench.status_code == 200
    assert r_bench.json()["overall_benchmark_score"] >= 85.0


def test_inspect_upload_endpoint():
    # Test multipart form upload with a mock image file
    fake_img = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4"
    files = {"file": ("volunteer_field_photo.png", fake_img, "image/png")}
    data = {"transcript": "Culvert C-14 has 75% silt blockage."}
    response = client.post("/api/inspect/upload", files=files, data=data)
    assert response.status_code == 200
    res = response.json()
    assert "inspection_id" in res
    assert len(res["defects_detected"]) >= 1


def test_inspect_base64_endpoint():
    tiny_png_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    payload = {
        "transcript": "Retaining wall BW-07 shows 18.5 deg deflection.",
        "image_base64": tiny_png_b64,
        "image_filename": "wall_test.png",
    }
    response = client.post("/api/inspect", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert len(res["defects_detected"]) >= 1


def test_cascade_simulate_custom_defects():
    payload = {
        "gpm_rain_rate_mm_hr": 35.0,
        "sentinel1_soil_saturation": 0.60,
        "copernicus_dem_slope_deg": 18.0,
        "scenario_id": "test_moderate",
        "defects": [
            {
                "defect_id": "D-CUST-1",
                "defect_type": "culvert_siltation",
                "severity": "MEDIUM",
                "confidence": 0.9,
                "asset_id": "CULVERT_C14",
                "siltation_pct": 40.0,
            }
        ],
    }
    response = client.post("/api/cascade/simulate", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["scenario_id"] == "test_moderate"
    assert len(res["stages"]) == 5

