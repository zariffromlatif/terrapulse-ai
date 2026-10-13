"""Unit tests for Verification & Risk Engine."""

import pytest
from proofpath.extractor import EvidenceExtractor
from proofpath.verification import VerificationEngine


def test_verification_impersonation_contradiction():
    extractor = EvidenceExtractor()
    engine = VerificationEngine()

    chat = extractor.process_file_content(
        "police_threat.txt",
        b"I am Bangladesh Bank Officer. Transfer funds immediately within 30 min.",
        "text/plain",
    )
    receipt = extractor.process_file_content(
        "p2p_receipt.txt",
        b"Sent money to personal wallet: 01712345678. Amount: BDT 10,000.00.",
        "text/plain",
    )

    assessment, chronology = engine.verify_case([chat, receipt])

    assert assessment.risk_level in ("CRITICAL", "HIGH")
    assert assessment.risk_score >= 60.0
    contra_rules = [c.rule_id for c in assessment.contradictions]
    assert "RULE_IMPERSONATION_PERSONAL_P2P" in contra_rules
    assert len(chronology) >= 2


def test_verification_temporal_anomaly():
    extractor = EvidenceExtractor()
    engine = VerificationEngine()

    chat = extractor.process_file_content(
        "chat_start.txt",
        b"Hello. First contacted on 2026-10-20 10:00:00.",
        "text/plain",
    )
    receipt = extractor.process_file_content(
        "receipt_old.txt",
        b"Voucher TrxID: TX123 Amount: BDT 5000 Date: 2026-10-10 10:00:00",
        "text/plain",
    )

    assessment, _ = engine.verify_case([chat, receipt])
    contra_rules = [c.rule_id for c in assessment.contradictions]
    assert "RULE_TEMPORAL_ANOMALY_BACKDATED" in contra_rules


def test_verification_amount_mismatch():
    extractor = EvidenceExtractor()
    engine = VerificationEngine()

    chat = extractor.process_file_content(
        "chat.txt",
        b"Please deposit BDT 2000 registration fee.",
        "text/plain",
    )
    receipt = extractor.process_file_content(
        "receipt.txt",
        b"Transaction Amount: BDT 25,000.00 TrxID: BL882299",
        "text/plain",
    )

    assessment, _ = engine.verify_case([chat, receipt])
    contra_rules = [c.rule_id for c in assessment.contradictions]
    assert "RULE_AMOUNT_INCONSISTENCY" in contra_rules


def test_verification_amount_year_not_false_positive():
    extractor = EvidenceExtractor()
    engine = VerificationEngine()

    chat = extractor.process_file_content(
        "chat_no_amt.txt",
        b"Caller: Please transfer money to verification account. Time: 2026-10-12 11:30:00",
        "text/plain",
    )
    receipt = extractor.process_file_content(
        "receipt_25k.txt",
        b"TrxID: TXN111 Amount: BDT 25000 Date: 2026-10-12 11:45:00",
        "text/plain",
    )

    assessment, _ = engine.verify_case([chat, receipt])
    contra_rules = [c.rule_id for c in assessment.contradictions]
    # Year 2026 must NOT be misidentified as an amount
    assert "RULE_AMOUNT_INCONSISTENCY" not in contra_rules


def test_verification_strict_chronological_ordering():
    extractor = EvidenceExtractor()
    engine = VerificationEngine()

    c1 = extractor.process_file_content("c1.txt", b"First contact at 2026-10-12 10:00:00", "text/plain")
    r1 = extractor.process_file_content("r1.txt", b"TrxID: T1 Amount: BDT 5000 Date: 2026-10-12 10:30:00", "text/plain")
    c2 = extractor.process_file_content("c2.txt", b"Follow-up threat at 2026-10-12 11:00:00", "text/plain")
    r2 = extractor.process_file_content("r2.txt", b"TrxID: T2 Amount: BDT 10000 Date: 2026-10-12 11:30:00", "text/plain")

    _, chronology = engine.verify_case([c1, r1, c2, r2])

    assert len(chronology) == 4
    # Check sequence
    assert chronology[0].evidence_sources == ["c1.txt"]
    assert chronology[0].event_type == "INITIAL_COMMUNICATION"
    assert chronology[1].evidence_sources == ["r1.txt"]
    assert chronology[1].event_type == "PAYMENT_EXECUTION"
    assert chronology[2].evidence_sources == ["c2.txt"]
    assert chronology[2].event_type == "FOLLOWUP_COMMUNICATION"
    assert chronology[3].evidence_sources == ["r2.txt"]
    assert chronology[3].event_type == "PAYMENT_EXECUTION"


def test_verification_ampm_and_iso_timestamp_parsing():
    engine = VerificationEngine()
    dt1 = engine._parse_timestamp("2026-10-12 11:30 AM")
    assert dt1 is not None and dt1.hour == 11 and dt1.minute == 30

    dt2 = engine._parse_timestamp("12/10/2026 02:45 PM")
    assert dt2 is not None and dt2.hour == 14 and dt2.minute == 45

    dt3 = engine._parse_timestamp("2026-10-12T11:30:00Z")
    assert dt3 is not None and dt3.hour == 11

    dt4 = engine._parse_timestamp("12 Oct 2026 10:00:00")
    assert dt4 is not None and dt4.day == 12 and dt4.month == 10

