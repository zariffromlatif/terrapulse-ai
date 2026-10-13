"""Unit tests for Settlement Digital Twin & Topographic Hydro-Graph."""

import pytest
from terrapulse.digital_twin import CampDigitalTwin, haversine_distance_meters
from terrapulse.models import AssetStatus, AssetType, SettlementAsset


def test_distance_calculation():
    # Known distance test
    d = haversine_distance_meters(21.19882, 92.15340, 21.19895, 92.15320)
    assert 20.0 < d < 30.0


def test_digital_twin_topology():
    twin = CampDigitalTwin(block_name="Camp 4 Block G")
    # Verify core assets are registered
    assert "CULVERT_C14" in twin.assets
    assert "WALL_BW07" in twin.assets
    assert "LATRINE_LP101" in twin.assets
    assert "TUBEWELL_TW04" in twin.assets
    assert "SAFEZONE_SZ01" in twin.assets

    assert twin.graph.number_of_nodes() >= 25
    assert twin.graph.number_of_edges() >= 25
    assert twin.hydro_graph.number_of_edges() > 0


def test_hydrological_gravity_flow():
    twin = CampDigitalTwin()
    # Flow direction must flow from higher elevation to lower elevation
    for u, v, data in twin.hydro_graph.edges(data=True):
        elev_u = twin.assets[u].elevation_m
        elev_v = twin.assets[v].elevation_m
        assert elev_u > elev_v
        assert data["drop_m"] > 0


def test_topographic_wetness_index():
    twin = CampDigitalTwin()
    twi = twin.calculate_topographic_wetness_index()
    assert len(twi) == len(twin.assets)
    # Culvert C-14 is in a lower drainage gully with high catchment accumulation, TWI should be positive
    assert twi["CULVERT_C14"] > 0
    assert all(isinstance(val, float) for val in twi.values())


def test_sphere_wash_violations_detection():
    twin = CampDigitalTwin()
    violations = twin.detect_sphere_wash_violations()
    assert len(violations) >= 1

    # Check for the critical violation between LP101 and TW04
    critical_violation = next((v for v in violations if v.latrine_id == "LATRINE_LP101" and v.tubewell_id == "TUBEWELL_TW04"), None)
    assert critical_violation is not None
    assert critical_violation.distance_meters < 30.0
    assert critical_violation.minimum_required_meters == 30.0


def test_safe_evacuation_routing():
    twin = CampDigitalTwin()
    threatened_shelters = ["SHELTER_S408", "SHELTER_S409"]
    hazardous = {"WALL_BW07", "CULVERT_C14"}

    routes = twin.find_safe_evacuation_routes(threatened_shelters, hazardous)
    assert len(routes) == 2
    for r in routes:
        assert r["safe_zone_id"] in ["SAFEZONE_SZ01", "SAFEZONE_SZ02"]
        # Route should avoid the hazardous retaining wall and culvert
        assert "WALL_BW07" not in r["path_node_ids"]
        assert "CULVERT_C14" not in r["path_node_ids"]
        assert r["transit_distance_m"] > 0
        assert r["estimated_minutes"] > 0


def test_geojson_export():
    twin = CampDigitalTwin()
    geo = twin.export_geojson()
    assert geo["type"] == "FeatureCollection"
    assert "metadata" in geo
    assert len(geo["features"]) > 0

    point_features = [f for f in geo["features"] if f["geometry"]["type"] == "Point"]
    line_features = [f for f in geo["features"] if f["geometry"]["type"] == "LineString"]
    assert len(point_features) == len(twin.assets)
    assert len(line_features) == twin.graph.number_of_edges()
