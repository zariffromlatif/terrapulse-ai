#!/usr/bin/env python3
"""ProofPath AI - Fraud-Response Benchmark Suite (eval_benchmark.py).

Measures:
1. Extraction accuracy (financial loss, currencies, transaction IDs, suspect indicators)
2. Cross-document consistency & contradiction detection
3. Fraud pattern classification & tactic detection
4. Procedural response quality & statutory compliance
5. Cross-case scam intelligence syndicate linking
"""

import sys
import json
from proofpath.benchmark import run_fraud_response_benchmark
from proofpath.service import ProofPathService


def main():
    print("=" * 72)
    print("  PROOFPATH AI - FRAUD-RESPONSE COMPREHENSIVE BENCHMARK (2026)")
    print("=" * 72)
    print("Initializing benchmark test scenarios (Bangladesh & Singapore)...")

    service = ProofPathService()
    report = run_fraud_response_benchmark(service)

    print("\n--- BENCHMARK SCORECARD ---")
    print(f"Total Evaluated Scenarios  : {report.total_cases}")
    print(f"Passed Scenarios           : {report.passed_cases} / {report.total_cases}")
    print("-" * 72)
    print(f"1. Extraction Accuracy               : {report.extraction_accuracy}%")
    print(f"2. Cross-Doc Consistency & Anomalies : {report.consistency_detection_score}%")
    print(f"3. Fraud Pattern Classification      : {report.pattern_detection_score}%")
    print(f"4. Procedural Statutory Compliance   : {report.procedural_quality_score}%")
    print(f"5. Syndicate Intelligence Precision  : {report.syndicate_match_score}%")
    print("-" * 72)
    print(f"OVERALL COMPOSITE BENCHMARK SCORE    : {report.overall_benchmark_score}%")
    print("=" * 72)

    print("\nScenario Breakdown:")
    for detail in report.case_details:
        status_str = "[PASS]" if detail["passed"] else "[FAIL]"
        print(f"  {status_str} {detail['case_name']}")
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
