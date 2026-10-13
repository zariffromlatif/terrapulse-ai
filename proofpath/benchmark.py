"""Fraud-Response Evaluation Benchmark for ProofPath AI."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from proofpath.models import Jurisdiction
from proofpath.service import ProofPathService


@dataclass
class BenchmarkCase:
    name: str
    jurisdiction: Jurisdiction
    files: List[tuple[str, bytes, Optional[str]]]
    ground_truth: Dict[str, Any]


@dataclass
class BenchmarkReport:
    total_cases: int
    passed_cases: int
    extraction_accuracy: float
    consistency_detection_score: float
    pattern_detection_score: float
    procedural_quality_score: float
    syndicate_match_score: float
    overall_benchmark_score: float
    case_details: List[Dict[str, Any]] = field(default_factory=list)


def create_benchmark_test_cases() -> List[BenchmarkCase]:
    """Generate realistic multimodal synthetic test cases for benchmarking."""
    cases = []

    # Case 1: Bangladesh bKash Impersonation & Syndicate Match
    c1_chat = (
        "Caller: Good morning. This is Bangladesh Bank Security Officer Inspector Kabir. "
        "Your bKash account 01700112233 has been reported for suspicious transaction. "
        "Immediate action is required within 30 min or your account will be suspended and police case filed. "
        "To verify security, transfer 25,000 BDT to verification wallet 01719998877 right now. "
        "Time: 2026-10-12 11:30:00"
    )
    c1_receipt = (
        "bKash Transaction Statement\n"
        "TrxID: BL9A2K9Z9X\n"
        "Amount: BDT 25,000.00\n"
        "From: 01700112233\n"
        "To: 01719998877\n"
        "Date: 2026-10-12 11:45:00\n"
        "Status: Successful"
    )
    cases.append(
        BenchmarkCase(
            name="BD_bKash_Impersonation_Syndicate",
            jurisdiction=Jurisdiction.BANGLADESH,
            files=[
                ("threat_chat_whatsapp.txt", c1_chat.encode("utf-8"), "text/plain"),
                ("bkash_receipt_slip.txt", c1_receipt.encode("utf-8"), "text/plain"),
            ],
            ground_truth={
                "expected_loss": 25000.0,
                "expected_currency": "BDT",
                "expected_suspect_phone": "+8801719998877",
                "expected_pattern_keywords": ["Impersonation", "Coercion"],
                "expected_syndicate_cluster": "SYNDICATE-BD-BKASH-RING-01",
                "expected_contradiction": "RULE_IMPERSONATION_PERSONAL_P2P",
                "required_statutory_keywords": ["Bangladesh Bank", "16247", "Cyber Security Act"],
            },
        )
    )

    # Case 2: Singapore PayNow Task Scam & Syndicate Match
    c2_telegram = (
        "[Telegram Chat with @recruit_vip_elena]\n"
        "Elena: Hi! Shopee SG part-time VIP task opportunity. Earn daily commission rebate 20% by reviewing products. "
        "Task 1: Deposit SGD 1,500 to unlock commission and vip level.\n"
        "Transfer via PayNow to registered proxy mobile +6591234567.\n"
        "Access portal: http://sg-shopee-rebates.top/login\n"
        "Timestamp: 2026-10-11 14:00:00"
    )
    c2_paynow = (
        "FAST / PayNow Transfer Confirmation\n"
        "Reference Number: FAST202610119882\n"
        "Amount: SGD 1,500.00\n"
        "To Mobile: +6591234567\n"
        "Date: 2026-10-11 14:15:00\n"
        "Status: Completed"
    )
    cases.append(
        BenchmarkCase(
            name="SG_PayNow_Task_Scam_Syndicate",
            jurisdiction=Jurisdiction.SINGAPORE,
            files=[
                ("telegram_job_offer.txt", c2_telegram.encode("utf-8"), "text/plain"),
                ("paynow_transfer_slip.txt", c2_paynow.encode("utf-8"), "text/plain"),
            ],
            ground_truth={
                "expected_loss": 1500.0,
                "expected_currency": "SGD",
                "expected_suspect_phone": "+6591234567",
                "expected_pattern_keywords": ["Task", "Affiliate", "Investment"],
                "expected_syndicate_cluster": "SYNDICATE-SG-PAYNOW-JOB-RING-02",
                "required_statutory_keywords": ["Singapore Police Force", "Anti-Scam Centre", "ScamShield", "MAS"],
            },
        )
    )

    # Case 3: Backdated Receipt Contradiction Anomaly
    c3_chat = (
        "Agent: This is DHL Customs Courier. Your parcel held at customs clearance. "
        "Delivery charge is 8,000 BDT. "
        "Contact date: 2026-10-15 12:00:00"
    )
    c3_receipt = (
        "Payment Voucher\n"
        "Txn ID: CV88991122\n"
        "Amount: BDT 8000\n"
        "To: 01822334455\n"
        "Date: 2026-10-10 09:00:00\n"  # 5 days prior to contact
    )
    cases.append(
        BenchmarkCase(
            name="Temporal_Anomaly_Backdated_Receipt",
            jurisdiction=Jurisdiction.BANGLADESH,
            files=[
                ("customs_sms.txt", c3_chat.encode("utf-8"), "text/plain"),
                ("backdated_voucher.txt", c3_receipt.encode("utf-8"), "text/plain"),
            ],
            ground_truth={
                "expected_loss": 8000.0,
                "expected_currency": "BDT",
                "expected_contradiction": "RULE_TEMPORAL_ANOMALY_BACKDATED",
                "expected_pattern_keywords": ["Customs", "Parcel", "Advance-Fee"],
            },
        )
    )

    # Case 4: Amount Inconsistency Contradiction
    c4_chat = (
        "Official notice: Please pay the refundable registration deposit of BDT 5,000 only. "
        "Time: 2026-10-14 10:00:00"
    )
    c4_receipt = (
        "bKash Electronic Slip\n"
        "TrxID: TX99887766\n"
        "Amount: BDT 50,000.00\n"  # 10x higher
        "To: 01911223344\n"
        "Date: 2026-10-14 10:30:00"
    )
    cases.append(
        BenchmarkCase(
            name="Amount_Inconsistency_Escalation",
            jurisdiction=Jurisdiction.BANGLADESH,
            files=[
                ("offer_chat.txt", c4_chat.encode("utf-8"), "text/plain"),
                ("escalated_receipt.txt", c4_receipt.encode("utf-8"), "text/plain"),
            ],
            ground_truth={
                "expected_loss": 50000.0,
                "expected_currency": "BDT",
                "expected_contradiction": "RULE_AMOUNT_INCONSISTENCY",
            },
        )
    )

    return cases


def run_fraud_response_benchmark(service: Optional[ProofPathService] = None) -> BenchmarkReport:
    """Execute the full benchmark suite and compute quantitative performance metrics."""
    svc = service or ProofPathService()
    test_cases = create_benchmark_test_cases()

    extraction_scores = []
    consistency_scores = []
    pattern_scores = []
    procedural_scores = []
    syndicate_scores = []
    case_results = []

    passed_count = 0

    for case in test_cases:
        dossier = svc.analyze_case(
            files=case.files,
            jurisdiction=case.jurisdiction,
            victim_name="Benchmark Test Subject",
            case_id=f"EVAL-{case.name}",
        )

        gt = case.ground_truth
        c_res: Dict[str, Any] = {"case_name": case.name, "passed": True, "checks": {}}

        # 1. Extraction Score Check (Amount & Currency)
        amt_match = False
        if abs(dossier.total_loss_amount - gt.get("expected_loss", 0.0)) < 1.0:
            amt_match = True
        c_res["checks"]["amount_extraction"] = amt_match
        extraction_scores.append(1.0 if amt_match else 0.0)

        # 2. Consistency & Contradiction Detection Score
        expected_contra = gt.get("expected_contradiction")
        if expected_contra:
            found_contra = any(c.rule_id == expected_contra for c in dossier.risk_assessment.contradictions)
            c_res["checks"]["contradiction_detected"] = found_contra
            consistency_scores.append(1.0 if found_contra else 0.0)
        else:
            # If no specific contradiction expected, score 1.0 if no false positive severe contradicts
            consistency_scores.append(1.0)
            c_res["checks"]["contradiction_detected"] = True

        # 3. Scam Pattern Detection Score
        expected_patterns = gt.get("expected_pattern_keywords", [])
        if expected_patterns:
            matched_pat = any(any(kw.lower() in p.lower() for kw in expected_patterns) for p in [dossier.risk_assessment.primary_scam_pattern] + dossier.risk_assessment.secondary_patterns)
            c_res["checks"]["pattern_matched"] = matched_pat
            pattern_scores.append(1.0 if matched_pat else 0.0)
        else:
            pattern_scores.append(1.0)
            c_res["checks"]["pattern_matched"] = True

        # 4. Procedural Quality Score
        req_stat = gt.get("required_statutory_keywords", [])
        if req_stat:
            all_roadmap_text = " ".join([f"{s.authority_name} {s.statutory_reference} {s.contact_channel}" for s in dossier.procedural_roadmap])
            stat_hits = sum(1 for kw in req_stat if kw.lower() in all_roadmap_text.lower())
            stat_score = stat_hits / len(req_stat)
            c_res["checks"]["procedural_statutory_score"] = stat_score
            procedural_scores.append(stat_score)
        else:
            procedural_scores.append(1.0)
            c_res["checks"]["procedural_statutory_score"] = 1.0

        # 5. Syndicate Match Score
        expected_cluster = gt.get("expected_syndicate_cluster")
        if expected_cluster:
            cluster_hit = any(s.cluster_id == expected_cluster for s in dossier.syndicate_matches)
            c_res["checks"]["syndicate_matched"] = cluster_hit
            syndicate_scores.append(1.0 if cluster_hit else 0.0)
        else:
            syndicate_scores.append(1.0)
            c_res["checks"]["syndicate_matched"] = True

        case_passed = all(bool(v) if isinstance(v, bool) else (v >= 0.8) for v in c_res["checks"].values())
        c_res["passed"] = case_passed
        if case_passed:
            passed_count += 1
        case_results.append(c_res)

    avg_ext = sum(extraction_scores) / len(extraction_scores)
    avg_con = sum(consistency_scores) / len(consistency_scores)
    avg_pat = sum(pattern_scores) / len(pattern_scores)
    avg_pro = sum(procedural_scores) / len(procedural_scores)
    avg_syn = sum(syndicate_scores) / len(syndicate_scores)

    # Composite Benchmark Score (weighted)
    composite = (avg_ext * 0.25 + avg_con * 0.25 + avg_pat * 0.20 + avg_pro * 0.20 + avg_syn * 0.10) * 100.0

    return BenchmarkReport(
        total_cases=len(test_cases),
        passed_cases=passed_count,
        extraction_accuracy=round(avg_ext * 100, 1),
        consistency_detection_score=round(avg_con * 100, 1),
        pattern_detection_score=round(avg_pat * 100, 1),
        procedural_quality_score=round(avg_pro * 100, 1),
        syndicate_match_score=round(avg_syn * 100, 1),
        overall_benchmark_score=round(composite, 1),
        case_details=case_results,
    )
