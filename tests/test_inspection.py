"""Unit tests for Multimodal Inspection Engine."""

import pytest
from terrapulse.inspection import MultimodalInspectionEngine
from terrapulse.models import DefectSeverity, DefectType


def test_inspection_engine_init():
    engine = MultimodalInspectionEngine(api_key=None)
    assert engine._client is None


def test_inspection_fallback_extraction():
    engine = MultimodalInspectionEngine(api_key=None)
    transcript = (
        "Volunteer notes: Culvert C-14 has 75% silt blockage with plastic debris. "
        "Retaining wall BW-07 shows 18.5 deg deflection above family shelters. "
        "Tubewell TW-04 concrete apron has 4.2cm fissure crack."
    )

    result = engine.analyze_inspection(text_transcript=transcript)
    assert result.inspection_id.startswith("INSP-")
    assert len(result.defects_detected) >= 3
    assert result.risk_score >= 0.70

    # Verify bamboo wall defect
    wall_defect = next((d for d in result.defects_detected if d.defect_type == DefectType.BAMBOO_WALL_DEFLECTION), None)
    assert wall_defect is not None
    assert wall_defect.deflection_angle_deg == 18.5
    assert wall_defect.severity == DefectSeverity.CRITICAL
    assert wall_defect.bounding_box is not None
    assert 0 <= wall_defect.bounding_box.ymin <= 1000

    # Verify culvert defect
    culv_defect = next((d for d in result.defects_detected if d.defect_type == DefectType.CULVERT_SILTATION), None)
    assert culv_defect is not None
    assert culv_defect.siltation_pct == 75.0
    assert culv_defect.severity == DefectSeverity.CRITICAL

    # Verify apron crack defect
    apron_defect = next((d for d in result.defects_detected if d.defect_type == DefectType.CRACKED_DRAINAGE_APRON), None)
    assert apron_defect is not None
    assert apron_defect.crack_width_cm == 4.2


def test_inspection_empty_input_defaults():
    engine = MultimodalInspectionEngine(api_key=None)
    # Empty input should still provide valid safe baseline defect telemetry for Camp 4 Block G
    result = engine.analyze_inspection()
    assert len(result.defects_detected) >= 2
    assert result.risk_score > 0.5
