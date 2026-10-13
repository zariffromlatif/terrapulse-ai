"""Unit tests for Dossier Generator (PDF, ZIP, Markdown)."""

import io
import zipfile
import pytest
from proofpath.models import Jurisdiction
from proofpath.service import ProofPathService


def test_dossier_pdf_generation():
    service = ProofPathService()
    chat = ("chat.txt", b"Suspicious offer. Pay BDT 10000. Date: 2026-10-10", "text/plain")
    receipt = ("receipt.txt", b"TrxID: TXN111 Amount: BDT 10,000 Date: 2026-10-10", "text/plain")

    dossier = service.analyze_case([chat, receipt], Jurisdiction.BANGLADESH, "Test Victim", "+8801700000000")
    pdf_bytes = service.get_pdf(dossier.case_id)

    assert pdf_bytes is not None
    assert len(pdf_bytes) > 1000
    # PDF magic number
    assert pdf_bytes.startswith(b"%PDF-")


def test_dossier_zip_packet():
    service = ProofPathService()
    chat = ("chat.txt", b"PayNow request SGD 500", "text/plain")
    receipt = ("receipt.txt", b"Reference FAST123 Amount: SGD 500", "text/plain")

    dossier = service.analyze_case([chat, receipt], Jurisdiction.SINGAPORE, "Lee Wei", "+6591234567")
    zip_bytes = service.get_zip(dossier.case_id)

    assert zip_bytes is not None
    assert len(zip_bytes) > 1000

    # Unpack zip to verify files
    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
        file_list = zf.namelist()
        assert any(f.endswith(".pdf") for f in file_list)
        assert any(f.endswith(".md") for f in file_list)
        assert any(f.endswith(".json") for f in file_list)
        assert "evidence_manifest.csv" in file_list
        assert any("complaint" in f for f in file_list)


def test_dossier_xml_escaping_in_pdf():
    service = ProofPathService()
    # Content with raw unescaped XML and angle brackets
    chat = ("chat.txt", b"Caller: Contact me at <hacker@scam.org> or fee < 500 BDT & penalty > 1000. Date: 2026-10-10", "text/plain")
    receipt = ("receipt.txt", b"TrxID: TXN111 Amount: BDT 500 Date: 2026-10-10", "text/plain")

    dossier = service.analyze_case([chat, receipt], Jurisdiction.BANGLADESH, "Victim <Confidential & Private>", "+8801700000000")
    # Manually inject an unclosed tag into description
    dossier.chronology[0].description = "Suspect said <waiting for authorization and left unclosed"

    pdf_bytes = service.dossier_generator.generate_pdf(dossier)
    assert pdf_bytes is not None
    assert pdf_bytes.startswith(b"%PDF-")


def test_dossier_many_exhibits_beyond_26():
    service = ProofPathService()
    files = []
    for i in range(28):
        files.append((f"evidence_{i}.txt", f"Record {i} - info".encode("utf-8"), "text/plain"))

    dossier = service.analyze_case(files, Jurisdiction.BANGLADESH, "Victim", "+8801700000000")
    md = service.dossier_generator.generate_markdown(dossier)
    assert "Exhibit A" in md
    assert "Exhibit Z" in md
    assert "Exhibit AA" in md
    assert "Exhibit AB" in md

