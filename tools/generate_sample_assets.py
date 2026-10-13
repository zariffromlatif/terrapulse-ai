"""Generator for realistic multimodal demo sample assets (PNG/PDF)."""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from PIL.PngImagePlugin import PngInfo
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

SAMPLES_DIR = Path(__file__).resolve().parent.parent / "proofpath" / "web" / "samples"
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)


def get_font(size: int, bold: bool = False):
    """Load system font if available, fallback to default."""
    font_name = "arialbd.ttf" if bold else "arial.ttf"
    try:
        return ImageFont.truetype(font_name, size)
    except Exception:
        try:
            return ImageFont.truetype("segoeui.ttf", size)
        except Exception:
            return ImageFont.load_default()


def create_bkash_slip():
    """Create authentic bKash Electronic Transaction Slip PNG."""
    width, height = 750, 1100
    img = Image.new("RGB", (width, height), color="#F4F5F7")
    draw = ImageDraw.Draw(img)

    # Header gradient / banner
    header_color = "#E2136E"  # bKash signature magenta
    draw.rectangle([(0, 0), (width, 160)], fill=header_color)

    font_title = get_font(32, bold=True)
    font_sub = get_font(18, bold=False)
    font_bold = get_font(20, bold=True)
    font_regular = get_font(18, bold=False)
    font_large_amt = get_font(44, bold=True)
    font_mono = get_font(18, bold=True)

    draw.text((40, 45), "bKash", fill="#FFFFFF", font=get_font(42, bold=True))
    draw.text((40, 100), "Electronic Transaction Statement / রসিদ", fill="#FFE4EE", font=font_sub)

    # Success badge card
    card_bg = "#FFFFFF"
    draw.rounded_rectangle([(40, 190), (width - 40, 360)], radius=16, fill=card_bg, outline="#E5E7EB", width=2)
    draw.ellipse([( width // 2 - 32, 215), (width // 2 + 32, 279)], fill="#10B981")
    draw.text((width // 2 - 14, 228), "✓", fill="#FFFFFF", font=get_font(32, bold=True))

    draw.text((width // 2 - 130, 290), "Send Money Successful", fill="#111827", font=font_bold)
    draw.text((width // 2 - 140, 320), "BDT 25,000.00", fill="#E2136E", font=font_large_amt)

    # Transaction Details Card
    detail_top = 390
    detail_bottom = 980
    draw.rounded_rectangle([(40, detail_top), (width - 40, detail_bottom)], radius=16, fill=card_bg, outline="#E5E7EB", width=2)

    fields = [
        ("Transaction ID (TrxID)", "BL9A2K9Z9X"),
        ("Recipient bKash Account (To)", "01719998877"),
        ("Sender Account (From)", "01712000000"),
        ("Transaction Date & Time", "2026-10-12 11:45:00"),
        ("Transfer Amount", "BDT 25,000.00"),
        ("Service Charge", "BDT 0.00"),
        ("Total Debited", "BDT 25,000.00"),
        ("Reference Note", "Emergency Clearance Desk"),
        ("Payment Status", "SUCCESSFUL"),
        ("Channel / Network", "MFS P2P Transfer (App v5.8)"),
    ]

    curr_y = detail_top + 30
    for label, val in fields:
        draw.text((70, curr_y), label, fill="#6B7280", font=font_regular)
        val_font = font_mono if "ID" in label or "Account" in label else font_bold
        val_color = "#10B981" if val == "SUCCESSFUL" else ("#111827" if "BDT" not in val else "#E2136E")
        draw.text((360, curr_y), val, fill=val_color, font=val_font)
        curr_y += 35
        draw.line([(70, curr_y), (width - 70, curr_y)], fill="#F3F4F6", width=1)
        curr_y += 20

    # Security Verification Seal
    draw.text((width // 2 - 180, 1020), "🛡️ Verified by bKash Digital Forensics Audit Log", fill="#9CA3AF", font=font_sub)
    draw.text((width // 2 - 140, 1050), "Document SHA-256 Digest Record", fill="#9CA3AF", font=get_font(14, bold=False))

    transcript_text = (
        "bKash Transaction Slip\n"
        "TrxID: BL9A2K9Z9X\n"
        "Amount: BDT 25,000.00\n"
        "To: 01719998877\n"
        "From: 01712000000\n"
        "Date: 2026-10-12 11:45:00\n"
        "Status: Successful\n"
        "Reference: Emergency Clearance Desk\n"
        "Channel: bKash MFS P2P"
    )

    png_info = PngInfo()
    png_info.add_text("Description", transcript_text)
    png_info.add_text("Comment", transcript_text)
    png_info.add_text("ForensicText", transcript_text)

    dest = SAMPLES_DIR / "bkash_transfer_slip.png"
    img.save(dest, format="PNG", pnginfo=png_info)
    print(f"Generated {dest}")


def create_paynow_slip():
    """Create authentic Singapore PayNow FAST Electronic Transfer Confirmation PNG."""
    width, height = 750, 1100
    img = Image.new("RGB", (width, height), color="#0F172A")
    draw = ImageDraw.Draw(img)

    # PayNow Maroon/Purple header bar
    header_color = "#7B1846"
    draw.rectangle([(0, 0), (width, 160)], fill=header_color)

    font_title = get_font(34, bold=True)
    font_sub = get_font(18, bold=False)
    font_bold = get_font(20, bold=True)
    font_regular = get_font(18, bold=False)
    font_large_amt = get_font(44, bold=True)
    font_mono = get_font(18, bold=True)

    draw.text((40, 45), "PayNow", fill="#FFFFFF", font=font_title)
    draw.text((40, 100), "ABS Electronic Funds Transfer / FAST Confirmation", fill="#FBCFE8", font=font_sub)

    card_bg = "#1E293B"
    draw.rounded_rectangle([(40, 190), (width - 40, 360)], radius=16, fill=card_bg, outline="#334155", width=2)
    draw.ellipse([(width // 2 - 32, 215), (width // 2 + 32, 279)], fill="#10B981")
    draw.text((width // 2 - 14, 228), "✓", fill="#FFFFFF", font=get_font(32, bold=True))

    draw.text((width // 2 - 110, 290), "Transfer Completed", fill="#F8FAFC", font=font_bold)
    draw.text((width // 2 - 140, 320), "SGD 1,500.00", fill="#38BDF8", font=font_large_amt)

    # Details card
    detail_top = 390
    detail_bottom = 980
    draw.rounded_rectangle([(40, detail_top), (width - 40, detail_bottom)], radius=16, fill=card_bg, outline="#334155", width=2)

    fields = [
        ("Reference Number", "FAST202610119882"),
        ("Transfer Mode", "PayNow to Mobile (FAST)"),
        ("Recipient Mobile (To)", "+6591234567"),
        ("Payer Name & Mobile", "Rachel Lim (+6598760000)"),
        ("Transaction Date & Time", "2026-10-11 14:15:00"),
        ("Transfer Amount", "SGD 1,500.00"),
        ("Fee / GST", "SGD 0.00"),
        ("Debit Account", "DBS Multi-Currency Account *8821"),
        ("Payment Purpose / Remarks", "Shopee VIP Level 2 Deposit"),
        ("Execution Status", "COMPLETED"),
    ]

    curr_y = detail_top + 30
    for label, val in fields:
        draw.text((70, curr_y), label, fill="#94A3B8", font=font_regular)
        val_font = font_mono if "Reference" in label or "Mobile" in label else font_bold
        val_color = "#34D399" if val == "COMPLETED" else ("#F8FAFC" if "SGD" not in val else "#38BDF8")
        draw.text((360, curr_y), val, fill=val_color, font=val_font)
        curr_y += 35
        draw.line([(70, curr_y), (width - 70, curr_y)], fill="#334155", width=1)
        curr_y += 20

    draw.text((width // 2 - 200, 1020), "🔒 Association of Banks in Singapore (ABS) Fast & Secure", fill="#64748B", font=font_sub)
    draw.text((width // 2 - 150, 1050), "Instant Clearing Switch Audit Record #9882", fill="#64748B", font=get_font(14, bold=False))

    transcript_text = (
        "PayNow Transfer Confirmation\n"
        "Reference Number: FAST202610119882\n"
        "Amount: SGD 1,500.00\n"
        "To Mobile: +6591234567\n"
        "Payer: Rachel Lim (+6598760000)\n"
        "Date: 2026-10-11 14:15:00\n"
        "Status: Completed\n"
        "Remarks: Shopee VIP Level 2 Deposit\n"
        "Method: PayNow"
    )

    png_info = PngInfo()
    png_info.add_text("Description", transcript_text)
    png_info.add_text("Comment", transcript_text)
    png_info.add_text("ForensicText", transcript_text)

    dest = SAMPLES_DIR / "paynow_transfer_slip.png"
    img.save(dest, format="PNG", pnginfo=png_info)
    print(f"Generated {dest}")


def create_whatsapp_chat():
    """Create realistic WhatsApp Threat & Coercion Chat Screenshot PNG."""
    width, height = 750, 1000
    img = Image.new("RGB", (width, height), color="#0B141A")  # WhatsApp Dark background
    draw = ImageDraw.Draw(img)

    # Top App Bar
    bar_color = "#1F2C34"
    draw.rectangle([(0, 0), (width, 100)], fill=bar_color)

    font_header = get_font(20, bold=True)
    font_sub = get_font(14, bold=False)
    font_msg = get_font(17, bold=False)
    font_bold_msg = get_font(17, bold=True)
    font_time = get_font(13, bold=False)

    # Back arrow + avatar icon
    draw.text((25, 38), "←", fill="#E9EDEF", font=get_font(24, bold=True))
    draw.ellipse([(60, 25), (110, 75)], fill="#EF4444")
    draw.text((75, 36), "👮", font=get_font(24, bold=False))

    draw.text((130, 28), "CID Cyber Crime & Police Dept", fill="#E9EDEF", font=font_header)
    draw.text((130, 56), "+8801719998877 • Law Enforcement Desk", fill="#8696A0", font=font_sub)

    # Encryption notice banner
    enc_box = [( width // 2 - 200, 130), (width // 2 + 200, 170)]
    draw.rounded_rectangle(enc_box, radius=8, fill="#182229")
    draw.text((width // 2 - 180, 142), "🔒 Messages and calls are end-to-end encrypted.", fill="#FFD279", font=get_font(13, bold=False))

    # Coercive Incoming Messages (Bubble style)
    messages = [
        (
            "🚨 OFFICIAL NOTICE: Bangladesh Bank & CID Cyber Crime Monitoring Cell.",
            "11:28 AM",
            False,
        ),
        (
            "Your bKash account (+8801712000000) has been linked to illegal illicit casino transactions. Under Section 23 of Digital Security Act, an arrest warrant has been prepared.",
            "11:29 AM",
            False,
        ),
        (
            "IMMEDIATE ACTION REQUIRED: Account will be suspended and frozen within 30 min unless verified via emergency clearance desk.",
            "11:30 AM",
            True,
        ),
        (
            "Transfer emergency clearance fee of BDT 25,000 to verification officer desk at 01719998877 immediately. Failure to comply will dispatch arrest team to your registered address.",
            "11:31 AM",
            True,
        ),
    ]

    curr_y = 200
    for text, time_str, is_urgent in messages:
        # Wrap text into lines
        words = text.split(" ")
        lines = []
        curr_line = []
        for w in words:
            curr_line.append(w)
            test_line = " ".join(curr_line)
            if draw.textlength(test_line, font=font_msg) > 520:
                curr_line.pop()
                lines.append(" ".join(curr_line))
                curr_line = [w]
        if curr_line:
            lines.append(" ".join(curr_line))

        bubble_h = len(lines) * 26 + 36
        bubble_w = 600
        bubble_bg = "#202C33" if not is_urgent else "#2A2B32"
        border_col = "#EF4444" if is_urgent else "#374151"

        draw.rounded_rectangle([(40, curr_y), (40 + bubble_w, curr_y + bubble_h)], radius=12, fill=bubble_bg, outline=border_col, width=1)

        line_y = curr_y + 14
        for l in lines:
            f = font_bold_msg if ("IMMEDIATE" in l or "BDT 25,000" in l or "OFFICIAL" in l) else font_msg
            col = "#FCA5A5" if is_urgent else "#E9EDEF"
            draw.text((60, line_y), l, fill=col, font=f)
            line_y += 26

        draw.text((40 + bubble_w - 75, curr_y + bubble_h - 22), time_str, fill="#8696A0", font=font_time)
        curr_y += bubble_h + 20

    transcript_text = (
        "Suspect: We are calling from Bangladesh Bank Fraud Monitoring Cell. "
        "Immediate action required! Your bKash account is linked to suspicious gambling transactions. "
        "Account will be locked within 30 min unless verified. "
        "Send emergency clearance fee of BDT 25,000 to verification desk at 01719998877 immediately. "
        "Time: 2026-10-12 11:30:00"
    )

    png_info = PngInfo()
    png_info.add_text("Description", transcript_text)
    png_info.add_text("Comment", transcript_text)
    png_info.add_text("ForensicText", transcript_text)

    dest = SAMPLES_DIR / "whatsapp_threat_chat.png"
    img.save(dest, format="PNG", pnginfo=png_info)
    print(f"Generated {dest}")


def create_telegram_chat():
    """Create realistic Telegram Task Scam Screenshot PNG."""
    width, height = 750, 1000
    img = Image.new("RGB", (width, height), color="#17212B")  # Telegram Dark background
    draw = ImageDraw.Draw(img)

    # Top App Bar
    bar_color = "#242F3D"
    draw.rectangle([(0, 0), (width, 100)], fill=bar_color)

    font_header = get_font(20, bold=True)
    font_sub = get_font(14, bold=False)
    font_msg = get_font(17, bold=False)
    font_bold_msg = get_font(17, bold=True)
    font_time = get_font(13, bold=False)

    draw.text((25, 38), "←", fill="#F5F5F5", font=get_font(24, bold=True))
    draw.ellipse([(60, 25), (110, 75)], fill="#2AABEE")
    draw.text((75, 36), "💼", font=get_font(24, bold=False))

    draw.text((130, 28), "Elena | Shopee VIP Regional Recruiter", fill="#F5F5F5", font=font_header)
    draw.text((130, 56), "@recruit_vip_elena • online", fill="#2AABEE", font=font_sub)

    messages = [
        (
            "Hi Rachel! Shopee Global Affiliate Task Program. Welcome to our remote merchant affiliate team!",
            "14:00",
            False,
        ),
        (
            "Earn daily commission rebate 20% on quick product rating & review tasks. Direct daily payout to bank!",
            "14:01",
            False,
        ),
        (
            "To activate your affiliate terminal and unlock VIP Level 2 rebate tier, deposit refundable capital of SGD 1,500.",
            "14:02",
            True,
        ),
        (
            "Please PayNow to our finance authorization mobile: +6591234567.\nAccess task portal: http://sg-shopee-rebates.top/login\nTimestamp: 2026-10-11 14:00:00",
            "14:03",
            True,
        ),
    ]

    curr_y = 140
    for text, time_str, is_highlight in messages:
        words = text.split(" ")
        lines = []
        curr_line = []
        for w in words:
            if "\n" in w:
                parts = w.split("\n")
                curr_line.append(parts[0])
                lines.append(" ".join(curr_line))
                curr_line = [parts[1]]
                continue
            curr_line.append(w)
            test_line = " ".join(curr_line)
            if draw.textlength(test_line, font=font_msg) > 520:
                curr_line.pop()
                lines.append(" ".join(curr_line))
                curr_line = [w]
        if curr_line:
            lines.append(" ".join(curr_line))

        bubble_h = len(lines) * 26 + 36
        bubble_w = 600
        bubble_bg = "#242F3D" if not is_highlight else "#1E2C3A"
        border_col = "#2AABEE" if is_highlight else "#2E3B4B"

        draw.rounded_rectangle([(40, curr_y), (40 + bubble_w, curr_y + bubble_h)], radius=12, fill=bubble_bg, outline=border_col, width=1)

        line_y = curr_y + 14
        for l in lines:
            f = font_bold_msg if ("SGD 1,500" in l or "+6591234567" in l or "sg-shopee" in l) else font_msg
            col = "#38BDF8" if ("http" in l or "+65" in l) else "#F5F5F5"
            draw.text((60, line_y), l, fill=col, font=f)
            line_y += 26

        draw.text((40 + bubble_w - 65, curr_y + bubble_h - 22), time_str, fill="#708499", font=font_time)
        curr_y += bubble_h + 20

    transcript_text = (
        "[Telegram @recruit_vip_elena]\n"
        "Elena: Hi Rachel! Shopee VIP Affiliate Task Opportunity. "
        "Earn daily commission rebate 20% on product review tasks. "
        "Deposit SGD 1,500 to unlock vip level.\n"
        "PayNow to mobile +6591234567.\n"
        "Portal: http://sg-shopee-rebates.top/login\n"
        "Timestamp: 2026-10-11 14:00:00"
    )

    png_info = PngInfo()
    png_info.add_text("Description", transcript_text)
    png_info.add_text("Comment", transcript_text)
    png_info.add_text("ForensicText", transcript_text)

    dest = SAMPLES_DIR / "telegram_task_scam.png"
    img.save(dest, format="PNG", pnginfo=png_info)
    print(f"Generated {dest}")


def create_employment_offer_pdf():
    """Create authentic fake employment offer letter PDF."""
    dest = SAMPLES_DIR / "fake_employment_offer.pdf"
    doc = SimpleDocTemplate(str(dest), pagesize=letter, leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("OfferTitle", parent=styles["Heading1"], fontSize=18, leading=22, textColor=colors.HexColor("#0F172A"), fontName="Helvetica-Bold", alignment=1)
    sub_style = ParagraphStyle("OfferSub", parent=styles["Normal"], fontSize=9, leading=13, textColor=colors.HexColor("#64748B"), alignment=1)
    body_style = ParagraphStyle("OfferBody", parent=styles["Normal"], fontSize=10, leading=15, textColor=colors.HexColor("#1E293B"))
    bold_style = ParagraphStyle("OfferBold", parent=body_style, fontName="Helvetica-Bold")
    table_header = ParagraphStyle("TableHeader", parent=body_style, fontName="Helvetica-Bold", textColor=colors.HexColor("#0F172A"))

    elements = []

    # Header letterhead
    elements.append(Paragraph("APEX GLOBAL COMMERCE PTE. LTD.", title_style))
    elements.append(Paragraph("UEN: 202619882K • 12 Marina Boulevard, Marina Bay Financial Centre Tower 2, Singapore 018983", sub_style))
    elements.append(Spacer(1, 12))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563EB"), spaceAfter=16))

    elements.append(Paragraph("<b>CONFIDENTIAL APPOINTMENT LETTER & REMOTE AFFILIATE CONTRACT</b>", ParagraphStyle("H2", parent=title_style, fontSize=13, leading=16, textColor=colors.HexColor("#1E40AF"))))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("<b>Date:</b> 11 October 2026<br/><b>To:</b> Rachel Lim (NRIC/FIN: S9876543A, Mobile: +6598760000)<br/><b>Reference:</b> AGC-SG-AFF-2026-9882", body_style))
    elements.append(Spacer(1, 14))

    elements.append(Paragraph("Dear Rachel Lim,", body_style))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(
        "We are pleased to formally offer you the contractual position of <b>Remote Product Review Specialist & Tier-2 Affiliate Partner</b> "
        "with Apex Global Commerce Pte. Ltd. You will collaborate on merchant rating optimization tasks across Southeast Asian e-commerce networks.",
        body_style
    ))
    elements.append(Spacer(1, 12))

    # Terms Table
    data = [
        [Paragraph("Contract Position", table_header), Paragraph("Remote E-Commerce Task Reviewer (Tier 2)", body_style)],
        [Paragraph("Commission Rebate Rate", table_header), Paragraph("20.0% Daily Rebate on completed task value", body_style)],
        [Paragraph("Security Capital Required", table_header), Paragraph("<b>SGD 1,500.00</b> (Mandatory activation deposit)", bold_style)],
        [Paragraph("Remittance Channel", table_header), Paragraph("PayNow to Treasury Mobile: <b>+6591234567</b>", bold_style)],
        [Paragraph("Work Portal Terminal", table_header), Paragraph("http://sg-shopee-rebates.top/login", body_style)],
        [Paragraph("Contract Date", table_header), Paragraph("2026-10-11 14:00:00", body_style)],
    ]

    t = Table(data, colWidths=[180, 320])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 16))

    elements.append(Paragraph(
        "<b>Terms of Activation:</b> In accordance with e-commerce syndicate compliance protocols, the initial refundable security capital of "
        "SGD 1,500.00 must be remitted via PayNow to registered corporate line <b>+6591234567</b> prior to account credential issuance. "
        "Upon task cycle completion, all principal deposits and accumulated rebates are remitted back daily.",
        body_style
    ))
    elements.append(Spacer(1, 24))

    # Signature block
    sig_data = [
        [Paragraph("<b>Executed for Apex Global Commerce Pte. Ltd.</b>", body_style), Paragraph("<b>Candidate Acknowledgment</b>", body_style)],
        [Paragraph("<font color='#2563EB'><i>[Digitally Signed: Marcus Vance]</i></font><br/>Marcus Vance, VP Regional Talent", body_style),
         Paragraph("Rachel Lim<br/>Accepted via Telegram @recruit_vip_elena", body_style)],
    ]
    st = Table(sig_data, colWidths=[250, 250])
    st.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(st)

    doc.build(elements)
    print(f"Generated {dest}")


def main():
    print(f"Generating authentic demo sample assets in {SAMPLES_DIR}...")
    create_bkash_slip()
    create_paynow_slip()
    create_whatsapp_chat()
    create_telegram_chat()
    create_employment_offer_pdf()
    print("All sample assets generated successfully.")


if __name__ == "__main__":
    main()
