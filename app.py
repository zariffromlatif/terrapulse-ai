"""ProofPath AI - Streamlit Web Dashboard.

Provides an interactive analyst portal to ingest multimodal evidence, inspect contradictions,
explore the scam intelligence knowledge graph, and export complaint dossiers.
"""

import io
import json
import streamlit as st
from proofpath.benchmark import run_fraud_response_benchmark
from proofpath.models import Jurisdiction
from proofpath.service import ProofPathService

st.set_page_config(
    page_title="ProofPath AI | Fraud Response Agent",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize service in session state
if "service" not in st.session_state:
    st.session_state.service = ProofPathService()

service = st.session_state.service

st.title("🛡️ ProofPath AI")
st.markdown(
    "**The AI agent that turns financial-fraud evidence into an actionable, evidence-backed response.**  \n"
    "*Google Cloud AI Builder Cup 2026 Submission*"
)

# Sidebar controls
st.sidebar.header("Investigation Setup")
jurisdiction_name = st.sidebar.selectbox(
    "Regulatory Jurisdiction",
    ["BANGLADESH", "SINGAPORE", "GENERAL"],
    help="Determines the statutory framework, financial regulatory ombudsman, and law enforcement escalation.",
)
jur_enum = getattr(Jurisdiction, jurisdiction_name, Jurisdiction.BANGLADESH)

victim_name = st.sidebar.text_input("Complainant Name", value="Farhan Ahmed")
victim_contact = st.sidebar.text_input("Complainant Contact", value="+8801700112233")

st.sidebar.markdown("---")
st.sidebar.subheader("⚡ Quick Demo Presets")

demo_action = None
if st.sidebar.button("🇧🇩 Load Bangladesh bKash Scam"):
    demo_action = "BD"
if st.sidebar.button("🇸🇬 Load Singapore PayNow Scam"):
    demo_action = "SG"
if st.sidebar.button("⚠️ Load Backdated Anomaly Case"):
    demo_action = "ANOMALY"

# Upload or Demo Data Preparation
files_to_process = []

if demo_action == "BD":
    c1 = (
        "Caller: Good morning. This is Bangladesh Bank Security Officer Inspector Kabir. "
        "Your bKash account 01700112233 has been reported for suspicious transaction. "
        "Immediate action is required within 30 min or your account will be suspended and police case filed. "
        "To verify security, transfer 25,000 BDT to verification wallet 01719998877 right now. "
        "Time: 2026-10-12 11:30:00"
    )
    c2 = (
        "bKash Transaction Statement\n"
        "TrxID: BL9A2K9Z9X\n"
        "Amount: BDT 25,000.00\n"
        "From: 01700112233\n"
        "To: 01719998877\n"
        "Date: 2026-10-12 11:45:00\n"
        "Status: Successful"
    )
    files_to_process = [
        ("threat_chat_whatsapp.txt", c1.encode("utf-8"), "text/plain"),
        ("bkash_receipt_slip.txt", c2.encode("utf-8"), "text/plain"),
    ]
    jur_enum = Jurisdiction.BANGLADESH

elif demo_action == "SG":
    c1 = (
        "[Telegram Chat with @recruit_vip_elena]\n"
        "Elena: Hi! Shopee SG part-time VIP task opportunity. Earn daily commission rebate 20% by reviewing products. "
        "Task 1: Deposit SGD 1,500 to unlock commission and vip level.\n"
        "Transfer via PayNow to registered proxy mobile +6591234567.\n"
        "Access portal: http://sg-shopee-rebates.top/login\n"
        "Timestamp: 2026-10-11 14:00:00"
    )
    c2 = (
        "FAST / PayNow Transfer Confirmation\n"
        "Reference Number: FAST202610119882\n"
        "Amount: SGD 1,500.00\n"
        "To Mobile: +6591234567\n"
        "Date: 2026-10-11 14:15:00\n"
        "Status: Completed"
    )
    files_to_process = [
        ("telegram_job_offer.txt", c1.encode("utf-8"), "text/plain"),
        ("paynow_transfer_slip.txt", c2.encode("utf-8"), "text/plain"),
    ]
    jur_enum = Jurisdiction.SINGAPORE

elif demo_action == "ANOMALY":
    c1 = "Agent: DHL Customs Courier. Parcel held at airport. Pay 8,000 BDT fee. Contact: 2026-10-15 12:00:00"
    c2 = "Payment Slip\nTxn ID: ANOMALY-88\nAmount: BDT 8000\nTo: 01822334455\nDate: 2026-10-10 09:00:00"
    files_to_process = [
        ("customs_sms.txt", c1.encode("utf-8"), "text/plain"),
        ("backdated_voucher.txt", c2.encode("utf-8"), "text/plain"),
    ]
    jur_enum = Jurisdiction.BANGLADESH

uploaded_files = st.file_uploader(
    "Upload suspicious messages, payment slips, receipts, audio transcripts, or documents",
    accept_multiple_files=True,
    help="Supports PNG, JPG, PDF, TXT, JSON",
)

if uploaded_files:
    files_to_process = [(f.name, f.read(), f.type) for f in uploaded_files]

if st.button("🚀 Ingest & Reconstruct Case Dossier", type="primary") or demo_action:
    if not files_to_process:
        st.warning("Please upload files or select one of the demo presets.")
    else:
        with st.spinner("Executing multimodal extraction, verification engine, and syndicate graph analysis..."):
            dossier = service.analyze_case(
                files=files_to_process,
                jurisdiction=jur_enum,
                victim_name=victim_name,
                victim_contact=victim_contact,
            )
            st.session_state.current_dossier = dossier

if "current_dossier" in st.session_state:
    dossier = st.session_state.current_dossier

    # High-level metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Verified Loss", f"{dossier.total_loss_currency} {dossier.total_loss_amount:,.2f}")
    with col2:
        st.metric("Assessed Risk Score", f"{dossier.risk_assessment.risk_level} ({dossier.risk_assessment.risk_score:.0f}/100)")
    with col3:
        st.metric("Primary Scam Pattern", dossier.risk_assessment.primary_scam_pattern)
    with col4:
        syn_count = len(dossier.syndicate_matches)
        st.metric("Syndicate Matches", f"{syn_count} Connected" if syn_count else "None (New Variant)")

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🔍 Verification & Contradictions",
        "⏱️ Chronology",
        "🕸️ Scam Intelligence Graph",
        "📑 Evidence Manifest",
        "📋 Procedural Roadmap",
        "✉️ Official Complaints",
        "📦 Export & Benchmark",
    ])

    with tab1:
        st.subheader("Executive Incident Summary")
        st.info(dossier.summary)

        st.subheader("Cross-Document Contradictions & Irregularities")
        if dossier.risk_assessment.contradictions:
            for c in dossier.risk_assessment.contradictions:
                with st.expander(f"⚠️ [{c.severity}] {c.title}", expanded=True):
                    st.write(c.description)
                    st.caption(f"Sources: {c.evidence_item_a} | {c.evidence_item_b or 'Single Artifact'}")
                    if c.conflicting_fields:
                        st.json(c.conflicting_fields)
        else:
            st.success("No cross-document contradictions detected.")

        st.subheader("Tactics & Red Flags")
        for rf in dossier.risk_assessment.red_flags:
            st.warning(rf)

    with tab2:
        st.subheader("Reconstructed Chronological Event Sequence")
        for ev in dossier.chronology:
            st.markdown(f"**Step {ev.sequence_number}** ({ev.timestamp or 'Timestamp Unspecified'} - `{ev.event_type}`)")
            st.write(ev.description)
            st.caption(f"Evidence Sources: {', '.join(ev.evidence_sources)}")
            st.divider()

    with tab3:
        st.subheader("Scam Intelligence Knowledge Graph")
        st.write("Network correlation of scam phone numbers, bank accounts, domains, and syndicate clusters:")
        graph_data = service.get_graph_data()
        st.write(f"Active Graph Metrics: **{graph_data['node_count']} nodes**, **{graph_data['edge_count']} links**")

        if dossier.syndicate_matches:
            st.error("🚨 Critical Syndicate Intelligence Match Detected")
            for sm in dossier.syndicate_matches:
                st.markdown(f"- **Syndicate:** `{sm.known_alias}` (Cluster ID: `{sm.cluster_id}`)")
                st.markdown(f"- **Confidence:** {sm.syndicate_confidence*100:.0f}% | **Matched Indicators:** `{', '.join(sm.matched_identifiers)}`")
                st.caption(sm.notes)
        else:
            st.info("No match in historical high-profile syndicate clusters. Case added to graph for future victim correlation.")

    with tab4:
        st.subheader("Evidence Exhibit Index & Cryptographic Hash Manifest")
        manifest_data = []
        for idx, item in enumerate(dossier.evidence_items):
            manifest_data.append({
                "Exhibit": f"Exhibit {chr(65 + idx)}",
                "Filename": item.filename,
                "Type": item.evidence_type.value,
                "SHA-256 Digest": item.sha256_hash[:16] + "...",
                "Integrity Status": "VERIFIED",
            })
        st.table(manifest_data)

    with tab5:
        st.subheader("Official Statutory Escalation Roadmap")
        for step in dossier.procedural_roadmap:
            with st.container():
                st.markdown(f"### Step {step.step_number}: [{step.timeline_window}] {step.authority_name}")
                st.caption(f"Statutory Basis: {step.statutory_reference}")
                st.write(f"**Contact Channel:** {step.contact_channel}")
                st.write(step.instructions)
                st.markdown(f"**Required Evidence:** {', '.join(step.required_evidence)}")
                st.divider()

    with tab6:
        st.subheader("Ready-to-File Official Complaint Letters")
        for draft in dossier.complaint_drafts:
            st.markdown(f"#### Application to: {draft.target_authority}")
            st.markdown(f"**Subject:** {draft.subject}")
            st.code(draft.body, language="text")

    with tab7:
        st.subheader("Download Evidence-Backed Case Package")
        pdf_bytes = service.get_pdf(dossier.case_id)
        zip_bytes = service.get_zip(dossier.case_id)

        col_a, col_b = st.columns(2)
        with col_a:
            if pdf_bytes:
                st.download_button(
                    "📄 Download Official PDF Dossier",
                    data=pdf_bytes,
                    file_name=f"ProofPath_Dossier_{dossier.case_id}.pdf",
                    mime="application/pdf",
                )
        with col_b:
            if zip_bytes:
                st.download_button(
                    "📦 Download Complete Evidence Package (ZIP)",
                    data=zip_bytes,
                    file_name=f"ProofPath_Package_{dossier.case_id}.zip",
                    mime="application/zip",
                )

        st.divider()
        st.subheader("Run Fraud-Response Evaluation Benchmark")
        if st.button("▶ Run Full Benchmark Suite"):
            with st.spinner("Running eval_benchmark suite..."):
                rep = run_fraud_response_benchmark(service)
                st.success(f"Benchmark Composite Score: {rep.overall_benchmark_score}%")
                st.json({
                    "overall_score": rep.overall_benchmark_score,
                    "extraction_accuracy": rep.extraction_accuracy,
                    "consistency_score": rep.consistency_detection_score,
                    "pattern_score": rep.pattern_detection_score,
                    "procedural_score": rep.procedural_quality_score,
                    "syndicate_score": rep.syndicate_match_score,
                    "case_details": rep.case_details,
                })
