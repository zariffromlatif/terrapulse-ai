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


def test_inspection_routine_survey_no_critical_false_positives():
    engine = MultimodalInspectionEngine(api_key=None)
    routine_text = "Routine check: Retaining walls intact. Drainage channels dry. Tubewell operational."
    result = engine.analyze_inspection(text_transcript=routine_text)

    assert result.risk_score <= 0.10
    assert "Stable" in result.primary_hazard or "Clear" in result.primary_hazard
    # None of the extracted defects should be CRITICAL or HIGH
    for d in result.defects_detected:
        assert d.severity == DefectSeverity.LOW


def test_inspection_medium_defects_calibration():
    engine = MultimodalInspectionEngine(api_key=None)
    text = "Culvert C-14 has 40% silt buildup from road runoff. Bamboo retaining wall BW-07 shows slight 6 degree deflection. No structural rupture."
    result = engine.analyze_inspection(text_transcript=text)

    wall = next((d for d in result.defects_detected if d.defect_type == DefectType.BAMBOO_WALL_DEFLECTION), None)
    assert wall is not None
    assert wall.deflection_angle_deg == 6.0
    assert wall.severity == DefectSeverity.MEDIUM

    culv = next((d for d in result.defects_detected if d.defect_type == DefectType.CULVERT_SILTATION), None)
    assert culv is not None
    assert culv.siltation_pct == 40.0
    assert culv.severity == DefectSeverity.MEDIUM


def test_inspection_base64_decoding():
    engine = MultimodalInspectionEngine(api_key=None)
    # 1x1 transparent PNG base64
    tiny_png_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    result = engine.analyze_inspection(
        text_transcript="Culvert C-14 inspection photo",
        image_base64=tiny_png_b64,
        image_filename="culvert_c14_drone.png",
    )
    assert len(result.defects_detected) >= 1

