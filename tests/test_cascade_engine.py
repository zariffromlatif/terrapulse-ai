"""Unit tests for Compound Disaster Cascade Reasoning Engine."""

import pytest
from terrapulse.cascade_engine import CompoundCascadeEngine
from terrapulse.digital_twin import CampDigitalTwin
from terrapulse.models import (
    BoundingBox,
    DefectSeverity,
    DefectType,
    InspectionDefect,
    OrbitalTelemetry,
)


def test_cascade_monsoon_simulation():
    twin = CampDigitalTwin()
    engine = CompoundCascadeEngine(digital_twin=twin)

    telemetry = OrbitalTelemetry(
        gpm_rain_rate_mm_hr=65.0,
        sentinel1_soil_saturation=0.88,
        copernicus_dem_slope_deg=22.5,
    )

    defects = [
        InspectionDefect(
            defect_id="D1",
            defect_type=DefectType.CULVERT_SILTATION,
            severity=DefectSeverity.CRITICAL,
            confidence=0.95,
            asset_id="CULVERT_C14",
            siltation_pct=75.0,
        ),
        InspectionDefect(
            defect_id="D2",
            defect_type=DefectType.BAMBOO_WALL_DEFLECTION,
            severity=DefectSeverity.CRITICAL,
            confidence=0.96,
            asset_id="WALL_BW07",
            deflection_angle_deg=18.5,
        ),
    ]

    res = engine.simulate_cascade(telemetry=telemetry, defects=defects)

    assert res.cascade_probability >= 0.85
    assert len(res.stages) == 5
    assert res.time_to_slope_failure_min < res.time_to_latrine_breach_min < res.time_to_water_contamination_min
    assert res.critical_interception_window_min > 0
    assert res.population_at_risk >= 450
    assert res.cholera_outbreak_risk_pct > 70.0
    assert len(res.sphere_violations) >= 1


def test_cascade_dry_baseline_simulation():
    twin = CampDigitalTwin()
    engine = CompoundCascadeEngine(digital_twin=twin)

    telemetry = OrbitalTelemetry(
        gpm_rain_rate_mm_hr=0.0,
        sentinel1_soil_saturation=0.20,
        copernicus_dem_slope_deg=22.5,
    )

    defects = [
        InspectionDefect(
            defect_id="D1",
            defect_type=DefectType.CULVERT_SILTATION,
            severity=DefectSeverity.LOW,
            confidence=0.9,
            asset_id="CULVERT_C14",
            siltation_pct=10.0,
        ),
    ]

    res = engine.simulate_cascade(telemetry=telemetry, defects=defects)
    # Dry conditions should result in low cascade probability
    assert res.cascade_probability < 0.40


def test_cascade_with_empty_defects():
    twin = CampDigitalTwin()
    engine = CompoundCascadeEngine(digital_twin=twin)

    telemetry = OrbitalTelemetry(
        gpm_rain_rate_mm_hr=0.0,
        sentinel1_soil_saturation=0.20,
        copernicus_dem_slope_deg=22.5,
    )

    # Empty defects must not trigger false disaster defaults (75% silt / 18.5 deg tilt)
    res = engine.simulate_cascade(telemetry=telemetry, defects=[])
    assert res.cascade_probability < 0.20
    assert res.population_at_risk == 0
    assert len(res.compromised_assets) == 0
    assert all(stg.status == "PENDING" for stg in res.stages)


def test_hydrological_rational_formula_runoff():
    twin = CampDigitalTwin()
    engine = CompoundCascadeEngine(digital_twin=twin)

    # Monsoon 65 mm/hr
    tel_rain = OrbitalTelemetry(gpm_rain_rate_mm_hr=65.0, sentinel1_soil_saturation=0.88)
    res_rain = engine.simulate_cascade(telemetry=tel_rain, defects=[])
    # Peak runoff for 65 mm/hr over 4200 m^2 with C=0.75 is approx 3.8 - 5.7 m^3/s
    assert "generates" in res_rain.stages[0].description
    assert "peak runoff" in res_rain.stages[0].description

    # Dry 0 mm/hr
    tel_dry = OrbitalTelemetry(gpm_rain_rate_mm_hr=0.0, sentinel1_soil_saturation=0.20)
    res_dry = engine.simulate_cascade(telemetry=tel_dry, defects=[])
    assert "No active runoff under dry conditions" in res_dry.stages[0].description

