#!/usr/bin/env python3
"""TerraPulse (CampTwin AI) - Quantitative Verification Benchmark Runner (eval_benchmark.py).

Measures:
1. Multimodal defect extraction accuracy & parameter precision.
2. Compound domino cascade prediction accuracy & time-to-failure physics.
3. UN Sphere Humanitarian Standard audit sensitivity (WASH 30m separation).
4. Micro-evacuation route safety & hazard avoidance.
5. Autonomous agent swarm dispatch coherence & humanitarian standards adherence.
"""

import sys
from terrapulse.benchmark import run_terrapulse_benchmark
from terrapulse.service import TerraPulseService


def main():
    print("=" * 76)
    print("  TERRAPULSE (CAMPTWIN AI) - COMPOUND DISASTER INTERCEPTOR BENCHMARK")
    print("  Google Cloud AI Builder Cup 2026 // Sustainability & Social Impact Track")
    print("  Target: Cox's Bazar Informal Settlement (Kutupalong Camp 4 Block G)")
    print("=" * 76)
    print("Initializing benchmark test scenarios across hydro-meteorological regimes...")

    service = TerraPulseService()
    report = run_terrapulse_benchmark(service)

    print("\n--- BENCHMARK SCORECARD ---")
    print(f"Total Evaluated Scenarios     : {report.total_evaluations}")
    print(f"Passed Scenarios              : {report.passed_evaluations} / {report.total_evaluations}")
    print("-" * 76)
    print(f"1. Multimodal Defect Extraction Accuracy  : {report.defect_extraction_accuracy}%")
    print(f"2. Compound Cascade Prediction Accuracy   : {report.cascade_prediction_accuracy}%")
    print(f"3. UN Sphere WASH 30m Audit Sensitivity   : {report.sphere_compliance_sensitivity}%")
    print(f"4. Micro-Evacuation Route Safety Score    : {report.evacuation_safety_score}%")
    print(f"5. Agent Swarm Dispatch Coherence Score   : {report.agent_swarm_coherence_score}%")
    print("-" * 76)
    print(f"OVERALL COMPOSITE BENCHMARK SCORE         : {report.overall_benchmark_score}%")
    print("=" * 76)

    print("\nScenario Breakdown:")
    for detail in report.scenario_details:
        status_str = "[PASS]" if detail["passed"] else "[FAIL]"
        print(f"  {status_str} {detail['name']} ({detail['case_id']})")
        for check, res in detail["checks"].items():
            print(f"         - {check}: {res}")

    if report.overall_benchmark_score >= 85.0:
        print("\n>>> BENCHMARK STATUS: ALL EVALUATION GATES PASSED (EXCELLENT)")
        sys.exit(0)
    else:
        print("\n>>> BENCHMARK STATUS: FAILED TO MEET ACCURACY THRESHOLD (MIN 85%)")
        sys.exit(1)


if __name__ == "__main__":
    main()
