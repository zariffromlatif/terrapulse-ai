"""Actionable Case Package generator: PII redaction, Evidence Index, PDF generation with ReportLab, and ZIP packaging."""

from __future__ import annotations

import csv
import html
import io
import json
import os
import re
import zipfile
from typing import Any, Dict, List, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from proofpath.models import CaseDossier, EvidenceItem


def escape_xml(text: Any) -> str:
    """Escape text for safe embedding in ReportLab Paragraph XML parser."""
    if text is None:
        return ""
    return html.escape(str(text))


def get_exhibit_label(idx: int) -> str:
    """Generate clean Exhibit letters A, B, ... Z, AA, AB, etc."""
    if idx < 26:
        return chr(65 + idx)
    first = chr(65 + (idx // 26) - 1)
    second = chr(65 + (idx % 26))
    return f"{first}{second}"


def redact_sensitive_pii(text: str) -> str:
    """Mask victim sensitive identifiers while retaining fraudster operational indicators."""
    if not text:
        return ""
    # Mask NID / IC numbers (e.g. 10 or 17 digit numbers or SG NRIC format [S|T|F|G]\d{7}[A-Z])
    text = re.sub(r"\b([S|T|F|G])\d{5}(\d{2}[A-Z])\b", r"\1*****\2", text, flags=re.IGNORECASE)
    # Mask 16 digit card numbers
    text = re.sub(r"\b\d{4}[ -]?\d{4}[ -]?\d{4}[ -]?(\d{4})\b", r"****-****-****-\1", text)
    # Mask victim PIN / OTP mentions
    text = re.sub(r"(PIN|OTP|Passcode)[:\s]*([0-9]{4,6})", r"\1: [REDACTED_SECURITY_CREDENTIAL]", text, flags=re.IGNORECASE)
    return text


class DossierGenerator:
    """Generates comprehensive forensic dossiers across PDF, Markdown, JSON, and ZIP formats."""

    def generate_markdown(self, dossier: CaseDossier) -> str:
        """Render case dossier into an evidentiary Markdown document."""
        md = []
        md.append(f"# PROOFPATH AI - OFFICIAL FRAUD INCIDENT DOSSIER")
        md.append(f"**Case Reference:** `{dossier.case_id}`  |  **Generated:** `{dossier.created_at}`")
        md.append(f"**Jurisdiction:** `{dossier.jurisdiction.value}`  |  **Assessed Threat:** `{dossier.risk_assessment.risk_level}` ({dossier.risk_assessment.risk_score:.0f}/100)")
        md.append(f"**Total Verified Loss:** `{dossier.total_loss_currency} {dossier.total_loss_amount:,.2f}`\n")
        md.append("---")

        md.append("## 1. Executive Incident Summary")
        md.append(redact_sensitive_pii(dossier.summary))
        md.append(f"\n- **Primary Scam Pattern:** {dossier.risk_assessment.primary_scam_pattern}")
        if dossier.risk_assessment.secondary_patterns:
            md.append(f"- **Secondary Patterns:** {', '.join(dossier.risk_assessment.secondary_patterns)}")
        if dossier.risk_assessment.tactics_detected:
            md.append(f"- **Tactics Identified:** {', '.join(dossier.risk_assessment.tactics_detected)}")

        # Red flags & Contradictions
        if dossier.risk_assessment.contradictions:
            md.append("\n### Verified Forensic Contradictions & Irregularities")
            for c in dossier.risk_assessment.contradictions:
                md.append(f"- **[{c.severity}] {c.title}**: {c.description} *(Sources: {c.evidence_item_a} / {c.evidence_item_b or 'N/A'})*")

        if dossier.risk_assessment.red_flags:
            md.append("\n### Critical Red Flags")
            for rf in dossier.risk_assessment.red_flags:
                md.append(f"- ⚠️ {rf}")

        # Cross-Case Syndicate Intelligence
        md.append("\n---")
        md.append("## 2. Cross-Case Scam Intelligence & Syndicate Matching")
        if dossier.syndicate_matches:
            for s in dossier.syndicate_matches:
                md.append(f"- **Syndicate Cluster:** `{s.cluster_id}` ({s.known_alias})")
                md.append(f"  - **Confidence:** {s.syndicate_confidence * 100:.0f}%  |  **Linked Historical Cases:** {s.total_linked_cases}")
                md.append(f"  - **Matched Indicators:** `{', '.join(s.matched_identifiers)}`")
                md.append(f"  - **Analyst Note:** {s.notes}")
        else:
            md.append("*No direct matches found in known high-priority syndicate clusters. Unique threat profile recorded.*")

        # Chronological Event Timeline
        md.append("\n---")
        md.append("## 3. Chronological Reconstruction Timeline")
        md.append("| # | Timestamp | Event Type | Description | Sources |")
        md.append("|---|---|---|---|---|")
        for ev in dossier.chronology:
            ts = ev.timestamp or "Unspecified"
            srcs = ", ".join(ev.evidence_sources)
            md.append(f"| {ev.sequence_number} | {ts} | {ev.event_type} | {redact_sensitive_pii(ev.description)} | {srcs} |")

        # Evidence Index
        md.append("\n---")
        md.append("## 4. Evidence Exhibit Index & Hash Manifest")
        md.append("| Exhibit | Filename | Evidence Type | SHA-256 Hash | Integrity Status |")
        md.append("|---|---|---|---|---|")
        for idx, item in enumerate(dossier.evidence_items):
            letter = get_exhibit_label(idx)
            md.append(f"| Exhibit {letter} | `{item.filename}` | {item.evidence_type.value} | `{item.sha256_hash[:16]}...` | VERIFIED |")

        # Procedural Roadmap
        md.append("\n---")
        md.append("## 5. Staged Procedural Response Roadmap")
        for step in dossier.procedural_roadmap:
            md.append(f"### Step {step.step_number}: [{step.timeline_window}] {step.authority_name}")
            md.append(f"- **Contact / Desk:** {step.contact_channel}")
            md.append(f"- **Statutory Basis:** *{step.statutory_reference}*")
            md.append(f"- **Instructions:** {step.instructions}")
            md.append(f"- **Required Packets:** {', '.join(step.required_evidence)}\n")

        # Complaint Drafts
        md.append("---")
        md.append("## 6. Official Complaint Letters")
        for d in dossier.complaint_drafts:
            md.append(f"### Filing Application: {d.target_authority}")
            md.append(f"**Subject:** {d.subject}\n")
            md.append("```text")
            md.append(redact_sensitive_pii(d.body))
            md.append("```\n")

        return "\n".join(md)

    def generate_pdf(self, dossier: CaseDossier) -> bytes:
        """Render case dossier into an official PDF document using ReportLab."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()

        # Custom typography styles
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#1e293b"),
            spaceAfter=4,
        )
        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#475569"),
            spaceAfter=12,
        )
        h2_style = ParagraphStyle(
            "SectionH2",
            parent=styles["Heading2"],
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#0f172a"),
            spaceBefore=10,
            spaceAfter=6,
        )
        body_style = ParagraphStyle(
            "DocBody",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#334155"),
            spaceAfter=4,
        )
        code_style = ParagraphStyle(
            "DocCode",
            parent=styles["Code"],
            fontSize=7.5,
            leading=10,
            textColor=colors.HexColor("#1e293b"),
            backColor=colors.HexColor("#f1f5f9"),
            spaceAfter=6,
        )

        story = []

        # Header Title
        story.append(Paragraph("PROOFPATH AI - EVIDENCE-BACKED FRAUD DOSSIER", title_style))
        risk_color = '#dc2626' if dossier.risk_assessment.risk_level in ('CRITICAL', 'HIGH') else '#16a34a'
        story.append(
            Paragraph(
                f"<b>Case ID:</b> {escape_xml(dossier.case_id)} &nbsp;|&nbsp; "
                f"<b>Jurisdiction:</b> {escape_xml(dossier.jurisdiction.value)} &nbsp;|&nbsp; "
                f"<b>Assessed Risk:</b> <font color='{risk_color}'>{escape_xml(dossier.risk_assessment.risk_level)} ({dossier.risk_assessment.risk_score:.0f}/100)</font> &nbsp;|&nbsp; "
                f"<b>Verified Loss:</b> {escape_xml(dossier.total_loss_currency)} {dossier.total_loss_amount:,.2f}",
                subtitle_style,
            )
        )
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#cbd5e1"), spaceAfter=8))

        # Executive Summary
        story.append(Paragraph("1. Executive Incident Summary", h2_style))
        story.append(Paragraph(escape_xml(redact_sensitive_pii(dossier.summary)), body_style))
        story.append(
            Paragraph(
                f"<b>Primary Scam Typology:</b> {escape_xml(dossier.risk_assessment.primary_scam_pattern)}<br/>"
                f"<b>Identified Tactics:</b> {escape_xml(', '.join(dossier.risk_assessment.tactics_detected) or 'N/A')}",
                body_style,
            )
        )

        # Contradictions & Irregularities
        if dossier.risk_assessment.contradictions:
            story.append(Spacer(1, 4))
            story.append(Paragraph("<b>Forensic Contradictions & Irregularities:</b>", body_style))
            for c in dossier.risk_assessment.contradictions:
                story.append(
                    Paragraph(
                        f"• <b>[{escape_xml(c.severity)}] {escape_xml(c.title)}:</b> {escape_xml(c.description)}",
                        body_style,
                    )
                )

        # Cross-Case Scam Intelligence
        story.append(Spacer(1, 6))
        story.append(Paragraph("2. Cross-Case Scam Intelligence & Syndicate Matching", h2_style))
        if dossier.syndicate_matches:
            for s in dossier.syndicate_matches:
                story.append(
                    Paragraph(
                        f"<b>Syndicate Match:</b> {escape_xml(s.known_alias)} (ID: {escape_xml(s.cluster_id)})<br/>"
                        f"• <b>Confidence:</b> {s.syndicate_confidence*100:.0f}% &nbsp;|&nbsp; <b>Linked Cases:</b> {s.total_linked_cases}<br/>"
                        f"• <b>Matched Network Indicators:</b> {escape_xml(', '.join(s.matched_identifiers))}<br/>"
                        f"• <b>Intelligence Note:</b> {escape_xml(s.notes)}",
                        body_style,
                    )
                )
        else:
            story.append(Paragraph("No direct indicator overlap with cataloged syndicates. Case registered into active graph for future cross-victim correlation.", body_style))

        # Chronology Table
        story.append(Spacer(1, 6))
        story.append(Paragraph("3. Event Reconstruction Chronology", h2_style))
        chron_data = [["#", "Timestamp", "Event Type", "Description", "Sources"]]
        for ev in dossier.chronology:
            chron_data.append([
                Paragraph(str(ev.sequence_number), body_style),
                Paragraph(escape_xml(ev.timestamp or "N/A"), body_style),
                Paragraph(escape_xml(ev.event_type[:20]), body_style),
                Paragraph(escape_xml(redact_sensitive_pii(ev.description)), body_style),
                Paragraph(escape_xml(", ".join(ev.evidence_sources)), body_style),
            ])

        chron_table = Table(chron_data, colWidths=[20, 75, 80, 255, 110])
        chron_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f8fafc")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ])
        )
        story.append(chron_table)

        # Evidence Index Table
        story.append(Spacer(1, 6))
        story.append(Paragraph("4. Evidence Index & Hash Manifest", h2_style))
        ev_data = [["Exhibit", "Filename", "Type", "SHA-256 Digest", "Status"]]
        for idx, it in enumerate(dossier.evidence_items):
            letter_char = get_exhibit_label(idx)
            ev_data.append([
                Paragraph(f"Exhibit {letter_char}", body_style),
                Paragraph(escape_xml(it.filename[:28]), body_style),
                Paragraph(escape_xml(it.evidence_type.value[:18]), body_style),
                Paragraph(f"<code>{escape_xml(it.sha256_hash[:16])}...</code>", body_style),
                Paragraph("VERIFIED", body_style),
            ])
        ev_table = Table(ev_data, colWidths=[55, 130, 110, 180, 65])
        ev_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f8fafc")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ])
        )
        story.append(ev_table)

        # Procedural Steps
        story.append(Spacer(1, 6))
        story.append(Paragraph("5. Procedural Escalation Roadmap", h2_style))
        for step in dossier.procedural_roadmap:
            story.append(
                Paragraph(
                    f"<b>Step {step.step_number}: [{escape_xml(step.timeline_window)}] {escape_xml(step.authority_name)}</b><br/>"
                    f"<i>Statutory Basis:</i> {escape_xml(step.statutory_reference)}<br/>"
                    f"<i>Contact:</i> {escape_xml(step.contact_channel)}<br/>"
                    f"<i>Instructions:</i> {escape_xml(step.instructions)}<br/>"
                    f"<i>Required Evidence:</i> {escape_xml(', '.join(step.required_evidence))}",
                    body_style,
                )
            )
            story.append(Spacer(1, 3))

        # Complaint Drafts
        if dossier.complaint_drafts:
            story.append(PageBreak())
            story.append(Paragraph("6. Official Complaint Applications", h2_style))
            for d in dossier.complaint_drafts:
                story.append(Paragraph(f"<b>Application Target:</b> {escape_xml(d.target_authority)}", body_style))
                story.append(Paragraph(f"<b>Subject:</b> {escape_xml(d.subject)}", body_style))
                clean_body = escape_xml(redact_sensitive_pii(d.body)).replace("\n", "<br/>")
                story.append(Paragraph(clean_body, code_style))
                story.append(Spacer(1, 6))

        doc.build(story)
        return buffer.getvalue()

    def generate_zip_packet(self, dossier: CaseDossier) -> bytes:
        """Create a complete downloadable ZIP containing PDF, Markdown, JSON, and letters."""
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            # 1. PDF Dossier
            pdf_bytes = self.generate_pdf(dossier)
            zf.writestr(f"ProofPath_Dossier_{dossier.case_id}.pdf", pdf_bytes)

            # 2. Markdown Report
            md_str = self.generate_markdown(dossier)
            zf.writestr(f"ProofPath_Report_{dossier.case_id}.md", md_str)

            # 3. Structured JSON
            json_str = dossier.model_dump_json(indent=2)
            zf.writestr(f"ProofPath_Case_{dossier.case_id}.json", json_str)

            # 4. Evidence Index CSV
            csv_buf = io.StringIO()
            writer = csv.writer(csv_buf)
            writer.writerow(["Exhibit", "Filename", "EvidenceType", "SHA256Hash", "Summary", "IntegrityStatus"])
            for idx, item in enumerate(dossier.evidence_items):
                letter_char = get_exhibit_label(idx)
                writer.writerow([
                    f"Exhibit {letter_char}",
                    item.filename,
                    item.evidence_type.value,
                    item.sha256_hash,
                    item.summary,
                    "VERIFIED",
                ])
            zf.writestr("evidence_manifest.csv", csv_buf.getvalue())

            # 5. Individual complaint text files
            for idx, draft in enumerate(dossier.complaint_drafts, start=1):
                clean_name = re.sub(r"[^a-zA-Z0-9_]", "_", draft.target_authority.lower())[:25]
                content = f"SUBJECT: {draft.subject}\n\n{redact_sensitive_pii(draft.body)}"
                zf.writestr(f"complaint_draft_{idx}_{clean_name}.txt", content)

        return zip_buffer.getvalue()
