"""Unit tests for Vertex AI Autonomous Agent Swarm."""

import pytest
from terrapulse.agents import (
    MicroEvacuationAgent,
    TacticalDispatchAgent,
    TerraPulseAgentSwarm,
    WASHProtectionAgent,
)
from terrapulse.cascade_engine import CompoundCascadeEngine
from terrapulse.digital_twin import CampDigitalTwin
from terrapulse.models import DefectType, InspectionDefect, OrbitalTelemetry


@pytest.fixture
def sample_cascade():
    twin = CampDigitalTwin()
    engine = CompoundCascadeEngine(digital_twin=twin)
    telemetry = OrbitalTelemetry(
        gpm_rain_rate_mm_hr=65.0,
        sentinel1_soil_saturation=0.88,
    )
    defects = [
        InspectionDefect(
            defect_id="D1",
            defect_type=DefectType.CULVERT_SILTATION,
            severity="CRITICAL",
            confidence=0.95,
            asset_id="CULVERT_C14",
            siltation_pct=75.0,
        ),
        InspectionDefect(
            defect_id="D2",
            defect_type=DefectType.BAMBOO_WALL_DEFLECTION,
            severity="CRITICAL",
            confidence=0.95,
            asset_id="WALL_BW07",
            deflection_angle_deg=18.5,
        ),
    ]
    return engine.simulate_cascade(telemetry=telemetry, defects=defects)


def test_tactical_dispatch_agent(sample_cascade):
    twin = CampDigitalTwin()
    agent = TacticalDispatchAgent(digital_twin=twin)
    missions = agent.generate_missions(sample_cascade)

    assert len(missions) >= 2
    # Verify culvert clearance mission
    c14_mission = next((m for m in missions if m.target_asset_id == "CULVERT_C14"), None)
    assert c14_mission is not None
    assert c14_mission.priority == "P1_IMMEDIATE"
    assert len(c14_mission.required_equipment) > 0
    assert "latitude" in c14_mission.target_gps


def test_wash_protection_agent(sample_cascade):
    twin = CampDigitalTwin()
    agent = WASHProtectionAgent(digital_twin=twin)
    alerts = agent.generate_alerts(sample_cascade)

    assert len(alerts) >= 1
    alert = alerts[0]
    assert alert.shutoff_required is True
    assert "TUBEWELL_TW04" in alert.affected_tubewells
    assert alert.aquatab_strips_needed > 0
    assert "Rohingya" in alert.boil_advisory_languages
    assert "Bengali" in alert.boil_advisory_languages


def test_micro_evacuation_agent(sample_cascade):
    twin = CampDigitalTwin()
    agent = MicroEvacuationAgent(digital_twin=twin)
    plans = agent.generate_plans(sample_cascade)

    assert len(plans) >= 1
    plan = plans[0]
    assert plan.plan_id == "EVAC-CORRIDOR-G1"
    assert "SAFEZONE" in plan.safe_zone_id
    assert len(plan.waypoint_coordinates) >= 3
    assert plan.estimated_transit_minutes > 0
    assert len(plan.avoided_hazard_zones) > 0
    assert "Rohingya" in plan.instructions_multilingual


def test_agent_swarm_consensus(sample_cascade):
    twin = CampDigitalTwin()
    swarm = TerraPulseAgentSwarm(digital_twin=twin)
    response = swarm.coordinate_interception(sample_cascade)

    assert len(response.tactical_missions) >= 2
    assert len(response.wash_alerts) >= 1
    assert len(response.evacuation_plans) >= 1
    assert response.un_sphere_compliance_score == 100.0
    assert response.swarm_coordination_status == "ACTIVE_INTERCEPTION"
