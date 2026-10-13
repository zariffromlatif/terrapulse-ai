"""Unit and integration tests for FastAPI REST API endpoints."""

import io
import pytest
from starlette.testclient import TestClient
from proofpath.api import app


@pytest.fixture
def client():
    return TestClient(app)


def test_api_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ProofPath AI"


def test_api_case_analysis_and_downloads(client):
    file1 = ("threat_chat.txt", b"Pay BDT 12000 urgently to 01712345678 within 30 min", "text/plain")
    file2 = ("receipt.txt", b"TrxID: 998877 Amount: BDT 12,000.00 Date: 2026-10-12 12:00:00", "text/plain")

    res = client.post(
        "/api/cases/analyze",
        data={
            "jurisdiction": "BANGLADESH",
            "victim_name": "Test User",
            "victim_contact": "+8801700112233",
        },
        files=[
            ("files", file1),
            ("files", file2),
        ],
    )

    assert res.status_code == 200
    data = res.json()
    case_id = data["case_id"]
    assert case_id is not None
    assert data["total_loss_amount"] == 12000.0
    assert data["total_loss_currency"] == "BDT"
    assert len(data["evidence_items"]) == 2

    # Test GET case
    get_res = client.get(f"/api/cases/{case_id}")
    assert get_res.status_code == 200
    assert get_res.json()["case_id"] == case_id

    # Test PDF download
    pdf_res = client.get(f"/api/cases/{case_id}/pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert pdf_res.content.startswith(b"%PDF-")

    # Test ZIP download
    zip_res = client.get(f"/api/cases/{case_id}/zip")
    assert zip_res.status_code == 200
    assert zip_res.headers["content-type"] == "application/zip"
    assert len(zip_res.content) > 500


def test_api_intelligence_graph(client):
    res = client.get("/api/intelligence/graph")
    assert res.status_code == 200
    data = res.json()
    assert "nodes" in data
    assert "edges" in data
    assert data["node_count"] > 0


def test_api_benchmark_endpoint(client):
    res = client.get("/api/benchmark/run")
    assert res.status_code == 200
    data = res.json()
    assert "overall_benchmark_score" in data
    assert data["overall_benchmark_score"] >= 85.0
