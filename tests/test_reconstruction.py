"""Unit tests for Multimodal Evidence Reconstruction and extraction."""

import hashlib
import pytest
from proofpath.dossier import redact_sensitive_pii
from proofpath.extractor import EvidenceExtractor
from proofpath.models import EvidenceType


def test_extractor_deterministic_receipt():
    extractor = EvidenceExtractor()
    content = (
        "bKash Electronic Transaction Slip\n"
        "TrxID: 9X9Z8Y7W6V\n"
        "Amount: BDT 15,000.00\n"
        "From: 01711223344\n"
        "To: 01899887766\n"
        "Date: 2026-10-12 14:00:00\n"
        "Status: Success"
    ).encode("utf-8")

    item = extractor.process_file_content("bkash_receipt.txt", content, "text/plain")

    assert item.filename == "bkash_receipt.txt"
    assert item.evidence_type == EvidenceType.TRANSACTION_RECEIPT
    assert item.sha256_hash == hashlib.sha256(content).hexdigest()
    assert len(item.extracted_transactions) >= 1
    tx = item.extracted_transactions[0]
    assert tx.transaction_id == "9X9Z8Y7W6V"
    assert tx.amount == 15000.0
    assert tx.currency == "BDT"
    assert tx.payment_method == "bKash"


def test_extractor_deterministic_chat():
    extractor = EvidenceExtractor()
    content = (
        "Suspect: Send money to +6591234567 immediately or DBS account locked. "
        "Visit phishing site at http://secure-dbs-auth.site/login"
    ).encode("utf-8")

    item = extractor.process_file_content("threat_chat.txt", content, "text/plain")

    assert item.evidence_type == EvidenceType.CHAT_MESSAGE
    phones = [e.normalized_value for e in item.extracted_entities if e.entity_type == "phone_number"]
    assert "+6591234567" in phones
    domains = [e.normalized_value for e in item.extracted_entities if e.entity_type == "domain"]
    assert any("secure-dbs-auth.site" in d for d in domains)

    # Coercion analysis layer verification
    coercion = item.metadata.get("coercion_analysis", {})
    assert coercion.get("urgency_detected") is True
    assert coercion.get("urgency_level") in ("HIGH", "MEDIUM")
    assert len(coercion.get("coercion_tactics", [])) >= 1


def test_extractor_empty_content_graceful():
    extractor = EvidenceExtractor()
    item = extractor.process_file_content("empty.txt", b"", "text/plain")
    assert item.filename == "empty.txt"
    assert item.sha256_hash == hashlib.sha256(b"").hexdigest()
    assert item.extracted_entities == []


def test_pii_redaction():
    text = "Complainant IC is S1234567A and Card is 4111-2222-3333-4444. OTP: 556677."
    redacted = redact_sensitive_pii(text)
    assert "S1234567A" not in redacted
    assert "4111-2222-3333-4444" not in redacted
    assert "556677" not in redacted
    assert "REDACTED" in redacted or "*****" in redacted


def test_extractor_multi_transaction_statement():
    extractor = EvidenceExtractor()
    content = (
        "bKash Account Statement\n"
        "Transaction 1:\n"
        "TrxID: BL9A111111 Amount: BDT 10,000.00 Date: 2026-10-12 10:00:00 To: 01719998877\n"
        "Transaction 2:\n"
        "TrxID: BL9A222222 Amount: BDT 15,000.00 Date: 2026-10-12 11:00:00 To: 01719998877\n"
    ).encode("utf-8")

    item = extractor.process_file_content("statement.txt", content, "text/plain")
    assert len(item.extracted_transactions) == 2
    assert item.extracted_transactions[0].transaction_id == "BL9A111111"
    assert item.extracted_transactions[0].amount == 10000.0
    assert item.extracted_transactions[1].transaction_id == "BL9A222222"
    assert item.extracted_transactions[1].amount == 15000.0


def test_extractor_mime_type_resolution(monkeypatch):
    extractor = EvidenceExtractor()
    item_mp3 = extractor.process_file_content("voicenote.mp3", b"audio-data")
    assert item_mp3.file_type == "audio/mp3"
    assert item_mp3.evidence_type == EvidenceType.VOICE_NOTE

    item_pdf = extractor.process_file_content("police_notice.pdf", b"pdf-data")
    assert item_pdf.file_type == "application/pdf"

    # Verify Vertex AI ADC initialization branch
    monkeypatch.setenv("GOOGLE_GENAI_USE_VERTEXAI", "true")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "mock-gcp-project")
    v_extractor = EvidenceExtractor()
    # In test environment without active GCP credentials, safely falls back to None with logged error
    assert v_extractor._client is None or hasattr(v_extractor._client, "models")


def test_extractor_sg_phone_no_bd_collision():
    extractor = EvidenceExtractor()
    # 01798765432 is a BD number whose 8-digit suffix 98765432 should not be treated as a Singapore phone
    item = extractor.process_file_content("bd_phone.txt", b"Send money to 01798765432", "text/plain")
    phones = [e.normalized_value for e in item.extracted_entities if e.entity_type == "phone_number"]
    assert "+8801798765432" in phones
    # Must NOT contain +6598765432
    assert "+6598765432" not in phones

