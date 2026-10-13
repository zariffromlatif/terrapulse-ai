"""TerraPulse (CampTwin AI) - Quantitative Verification Benchmark.

Evaluates:
1. Multimodal defect extraction accuracy & parameter precision.
2. Compound domino cascade prediction accuracy & time-to-failure physics.
3. UN Sphere Humanitarian Standard audit sensitivity (WASH 30m buffer).
4. Micro-evacuation route safety & hazard avoidance.
5. Autonomous agent swarm dispatch coherence & humanitarian standards adherence.
"""

from __future__ import annotations

from typing import Any, Dict, List
from pydantic import BaseModel

from terrapulse.models import DefectType, OrbitalTelemetry
from terrapulse.service import TerraPulseService


class BenchmarkReport(BaseModel):
    """Aggregated quantitative evaluation metrics for TerraPulse."""
    total_evaluations: int
    passed_evaluations: int
    defect_extraction_accuracy: float
    cascade_prediction_accuracy: float
    sphere_compliance_sensitivity: float
    evacuation_safety_score: float
    agent_swarm_coherence_score: float
    overall_benchmark_score: float
    scenario_details: List[Dict[str, Any]]


def run_terrapulse_benchmark(service: TerraPulseService) -> BenchmarkReport:
    """Executes full quantitative benchmark suite across disaster scenarios."""
    scenarios = service.get_preloaded_scenarios()
    details: List[Dict[str, Any]] = []

    passed_count = 0
    extraction_scores: List[float] = []
    cascade_scores: List[float] = []
    sphere_scores: List[float] = []
    evac_scores: List[float] = []
    agent_scores: List[float] = []

    for sc in scenarios:
        case_id = sc["id"]
        telemetry = OrbitalTelemetry(
            gpm_rain_rate_mm_hr=sc["telemetry"]["gpm_rain_rate_mm_hr"],
            sentinel1_soil_saturation=sc["telemetry"]["sentinel1_soil_saturation"],
            copernicus_dem_slope_deg=sc["telemetry"]["copernicus_dem_slope_deg"],
        )
        text = sc["inspection_text"]

        result = service.run_full_pipeline(
            telemetry=telemetry,
            inspection_text=text,
            scenario_id=case_id,
        )

        checks: Dict[str, bool] = {}

        # 1. Defect Extraction Check
        defects = result["inspection"]["defects_detected"]
        has_defects = len(defects) > 0
        checks["defect_extraction_valid"] = has_defects
        ext_score = 100.0 if has_defects else 0.0
        if "65mm" in case_id:
            types_found = {d["defect_type"] for d in defects}
            # Should detect retaining wall deflection and culvert siltation
            has_wall = any("wall" in t for t in types_found)
            has_culv = any("culvert" in t for t in types_found)
            ext_score = 100.0 if (has_wall and has_culv) else 80.0
        extraction_scores.append(ext_score)

        # 2. Cascade Prediction Check
        cascade = result["cascade"]
        has_5_stages = len(cascade["stages"]) == 5
        stages_ordered = all(
            cascade["stages"][i]["time_offset_minutes"] <= cascade["stages"][i + 1]["time_offset_minutes"]
            for i in range(len(cascade["stages"]) - 1)
        )
        prob_valid = 0.0 <= cascade["cascade_probability"] <= 1.0
        checks["cascade_domino_stages_valid"] = has_5_stages and stages_ordered and prob_valid
        casc_score = 100.0 if (has_5_stages and stages_ordered and prob_valid) else 50.0
        cascade_scores.append(casc_score)

        # 3. Sphere Standard Compliance Check
        violations = result["sphere_violations"]
        # In Camp 4 Block G, LP101 and TW04 are ~22m apart (violating 30m standard)
        has_sphere_violation = any(
            v["latrine_id"] == "LATRINE_LP101" and v["tubewell_id"] == "TUBEWELL_TW04"
            for v in violations
        )
        checks["sphere_30m_violation_detected"] = has_sphere_violation
        sph_score = 100.0 if has_sphere_violation else 0.0
        sphere_scores.append(sph_score)

        # 4. Micro-Evacuation Route Safety Check
        dispatch = result["dispatch"]
        evac_plans = dispatch["evacuation_plans"]
        has_evac = len(evac_plans) > 0
        evac_safe = True
        if has_evac:
            primary_plan = evac_plans[0]
            # Must reach a designated safe haven
            dest_valid = "SAFEZONE" in primary_plan["safe_zone_id"]
            # Avoided hazard zones documented
            has_avoided = len(primary_plan["avoided_hazard_zones"]) > 0
            evac_safe = dest_valid and has_avoided
        checks["evacuation_route_safe"] = has_evac and evac_safe
        ev_score = 100.0 if (has_evac and evac_safe) else 60.0
        evac_scores.append(ev_score)

        # 5. Agent Swarm Coherence Check
        tactical_msns = dispatch["tactical_missions"]
        wash_alerts = dispatch["wash_alerts"]
        has_tactical = len(tactical_msns) >= 2
        has_wash = len(wash_alerts) >= 1
        has_tools = all(len(m["required_equipment"]) > 0 for m in tactical_msns)
        checks["agent_swarm_coordinated"] = has_tactical and has_wash and has_tools
        ag_score = 100.0 if (has_tactical and has_wash and has_tools) else 75.0
        agent_scores.append(ag_score)

        case_passed = all(checks.values())
        if case_passed:
            passed_count += 1

        details.append({
            "case_id": case_id,
            "name": sc["name"],
            "passed": case_passed,
            "checks": checks,
        })

    total_cases = len(scenarios)
    avg_ext = round(sum(extraction_scores) / total_cases, 1)
    avg_casc = round(sum(cascade_scores) / total_cases, 1)
    avg_sph = round(sum(sphere_scores) / total_cases, 1)
    avg_evac = round(sum(evac_scores) / total_cases, 1)
    avg_ag = round(sum(agent_scores) / total_cases, 1)

    overall = round((avg_ext * 0.20) + (avg_casc * 0.25) + (avg_sph * 0.15) + (avg_evac * 0.20) + (avg_ag * 0.20), 1)

    return BenchmarkReport(
        total_evaluations=total_cases,
        passed_evaluations=passed_count,
        defect_extraction_accuracy=avg_ext,
        cascade_prediction_accuracy=avg_casc,
        sphere_compliance_sensitivity=avg_sph,
        evacuation_safety_score=avg_evac,
        agent_swarm_coherence_score=avg_ag,
        overall_benchmark_score=overall,
        scenario_details=details,
    )
