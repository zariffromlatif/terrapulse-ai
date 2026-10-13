"""Unit tests for Procedural Response Agent."""

import pytest
from proofpath.extractor import EvidenceExtractor
from proofpath.models import Jurisdiction, RiskAssessment
from proofpath.response_agent import ProceduralResponseAgent


def test_response_roadmap_bangladesh():
    agent = ProceduralResponseAgent()
    extractor = EvidenceExtractor()
    item = extractor.process_file_content("rcpt.txt", b"TrxID: 123 Amount: BDT 5000 To: 01712345678", "text/plain")
    assessment = RiskAssessment(
        risk_score=85.0,
        risk_level="CRITICAL",
        primary_scam_pattern="Impersonation",
        tactics_detected=["Urgency"],
    )

    roadmap = agent.generate_roadmap(Jurisdiction.BANGLADESH, [item], assessment, 5000.0, "BDT")
    assert len(roadmap) >= 3
    authorities = [s.authority_name for s in roadmap]
    assert any("bKash" in a or "Provider" in a for a in authorities)
    assert any("Police" in a or "CID" in a for a in authorities)
    assert any("Bangladesh Bank" in a or "CIPC" in a for a in authorities)


def test_response_roadmap_singapore():
    agent = ProceduralResponseAgent()
    extractor = EvidenceExtractor()
    item = extractor.process_file_content("rcpt_sg.txt", b"PayNow to +6591234567 Amount: SGD 1000", "text/plain")
    assessment = RiskAssessment(
        risk_score=90.0,
        risk_level="CRITICAL",
        primary_scam_pattern="Task Scam",
    )

    roadmap = agent.generate_roadmap(Jurisdiction.SINGAPORE, [item], assessment, 1000.0, "SGD")
    assert len(roadmap) >= 3
    authorities = [s.authority_name for s in roadmap]
    assert any("Anti-Scam" in a or "SPF" in a or "Kill-Switch" in a for a in authorities)
    assert any("ScamShield" in a for a in authorities)
    assert any("FIDReC" in a or "MAS" in a for a in authorities)


def test_complaint_drafts_generation():
    agent = ProceduralResponseAgent()
    extractor = EvidenceExtractor()
    item = extractor.process_file_content("rcpt.txt", b"TrxID: TXN999 Amount: BDT 20000", "text/plain")
    assessment = RiskAssessment(
        risk_score=75.0,
        risk_level="HIGH",
        primary_scam_pattern="Phishing",
    )

    drafts = agent.generate_complaint_drafts(
        jurisdiction=Jurisdiction.BANGLADESH,
        case_id="CASE-123",
        victim_name="Rahim Ali",
        victim_contact="+8801700000000",
        evidence_items=[item],
        risk_assessment=assessment,
        total_loss=20000.0,
        currency="BDT",
    )

    assert len(drafts) >= 2
    assert any("Provider" in d.target_authority or "Bank" in d.target_authority for d in drafts)
    assert any("Police" in d.target_authority or "CID" in d.target_authority for d in drafts)
    assert "CASE-123" in drafts[0].body
    assert "Rahim Ali" in drafts[0].body


def test_complaint_drafts_generation_general():
    agent = ProceduralResponseAgent()
    extractor = EvidenceExtractor()
    item = extractor.process_file_content("wire.txt", b"Transfer ID: SWIFT999 Amount: USD 5000", "text/plain")
    assessment = RiskAssessment(
        risk_score=80.0,
        risk_level="CRITICAL",
        primary_scam_pattern="Wire Fraud",
    )

    drafts = agent.generate_complaint_drafts(
        jurisdiction=Jurisdiction.GENERAL,
        case_id="CASE-INTL-101",
        victim_name="John Doe",
        victim_contact="+12025550199",
        evidence_items=[item],
        risk_assessment=assessment,
        total_loss=5000.0,
        currency="USD",
    )

    assert len(drafts) >= 2
    authorities = [d.target_authority for d in drafts]
    assert any("Wire Recall" in a or "Bank" in a for a in authorities)
    assert any("Cyber" in a for a in authorities)
    assert "CASE-INTL-101" in drafts[0].body
    assert "John Doe" in drafts[0].body

