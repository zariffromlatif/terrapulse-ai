"""Procedural Response Agent: Staged statutory escalation guidance for Bangladesh and Singapore."""

from __future__ import annotations

from typing import List, Optional
from proofpath.models import (
    ComplaintDraft,
    EvidenceItem,
    Jurisdiction,
    ProceduralStep,
    RiskAssessment,
)


class ProceduralResponseAgent:
    """Generates official statutory response roadmaps and legal complaint drafts."""

    def generate_roadmap(
        self,
        jurisdiction: Jurisdiction,
        evidence_items: List[EvidenceItem],
        risk_assessment: RiskAssessment,
        total_loss: float,
        currency: str,
    ) -> List[ProceduralStep]:
        """Generate time-sensitive procedural escalation steps based on statutory jurisdiction."""
        # Find primary suspect identifiers
        suspect_phones = []
        suspect_accounts = []
        txn_ids = []
        for it in evidence_items:
            for ent in it.extracted_entities:
                if ent.role == "suspect" and ent.entity_type == "phone_number":
                    suspect_phones.append(ent.normalized_value or ent.value)
            for tx in it.extracted_transactions:
                if tx.recipient_account:
                    suspect_accounts.append(tx.recipient_account)
                if tx.transaction_id:
                    txn_ids.append(tx.transaction_id)

        target_phone_str = ", ".join(list(set(suspect_phones))[:2]) or "Unspecified Suspect Number"
        target_acc_str = ", ".join(list(set(suspect_accounts))[:2]) or target_phone_str
        txn_str = ", ".join(list(set(txn_ids))[:2]) or "Disputed Transaction"

        if jurisdiction == Jurisdiction.BANGLADESH:
            return [
                ProceduralStep(
                    step_number=1,
                    stage="IMMEDIATE_FREEZE",
                    authority_name="Provider Dispute Desk (bKash 16247 / Nagad 16167 / Rocket 16216)",
                    contact_channel="Hotline: 16247 (bKash) / 16167 (Nagad) | Email: support@bkash.com",
                    timeline_window="0 - 2 Hours (Golden Window)",
                    instructions=(
                        f"Immediately call MFS/Bank customer support. Request emergency account freezing of recipient account "
                        f"({target_acc_str}) citing fraudulent transfer of {currency} {total_loss:,.2f} under TxID {txn_str}. "
                        f"Obtain a formal Complaint Ticket Number."
                    ),
                    required_evidence=["Transaction Receipt Screenshot", "Complaint Ticket Number", "Victim National ID"],
                    statutory_reference="Bangladesh Bank PSD Circular No. 06/2018 (Dispute Settlement in MFS)",
                ),
                ProceduralStep(
                    step_number=2,
                    stage="LAW_ENFORCEMENT_GD",
                    authority_name="Bangladesh Police Thana & CID Cyber Crime Investigation Division",
                    contact_channel="Nearest Police Station (Thana) | CID Hotline: 01320000888 | smscyber@police.gov.bd",
                    timeline_window="Within 24 Hours",
                    instructions=(
                        f"Lodge an official General Diary (GD) at your local Thana detailing fraudulent inducement by {target_phone_str}. "
                        f"Request the Duty Officer to forward the GD to the CID Cyber Police Centre for cyber trace and "
                        f"MFS wallet freeze clearance."
                    ),
                    required_evidence=["Printed Evidence Dossier", "GD Copy / Diary Reference", "NID Copy", "MFS Statement"],
                    statutory_reference="Cyber Security Act 2023 (Sections 24 & 26 - Fraudulent Impersonation & Extortion)",
                ),
                ProceduralStep(
                    step_number=3,
                    stage="REGULATOR_ESCALATION",
                    authority_name="Bangladesh Bank Customer Interests Protection Centre (CIPC)",
                    contact_channel="Hotline: 16236 | Email: bb.cipc@bb.org.bd | Motijheel, Dhaka",
                    timeline_window="Day 2 - Day 7",
                    instructions=(
                        f"Submit formal escalation to Bangladesh Bank CIPC if the MFS provider or commercial bank fails to "
                        f"sequester the fraudulent funds or complete arbitration within 10 working days. Attach the GD and Dossier."
                    ),
                    required_evidence=["Unresolved Provider Ticket", "Police GD Copy", "Full ProofPath Evidence Dossier"],
                    statutory_reference="Bangladesh Bank Financial Integrity & Customer Advisory Department (FICAD) Guidelines",
                ),
                ProceduralStep(
                    step_number=4,
                    stage="TELECOM_BLOCK",
                    authority_name="Bangladesh Telecommunication Regulatory Commission (BTRC)",
                    contact_channel="BTRC Consumer Complaints Hotline: 100 | portal.btrc.gov.bd",
                    timeline_window="Day 3 onwards",
                    instructions=(
                        f"Submit SIM blocking request for fraudulent caller {target_phone_str} to prevent further victim solicitation "
                        f"and mandate carrier verification of the fraudster's biometric SIM registration."
                    ),
                    required_evidence=["Call logs", "Threat message screenshots", "Police GD Number"],
                    statutory_reference="Bangladesh Telecommunication Regulation Act 2001 (Section 66)",
                ),
            ]

        elif jurisdiction == Jurisdiction.SINGAPORE:
            return [
                ProceduralStep(
                    step_number=1,
                    stage="IMMEDIATE_FREEZE",
                    authority_name="Bank 24/7 Anti-Scam Emergency Hotline / Emergency Kill-Switch",
                    contact_channel="DBS: 1800 339 6963 | OCBC: 1800 363 3333 | UOB: 1800 255 3955",
                    timeline_window="0 - 2 Hours (Golden Window)",
                    instructions=(
                        f"Activate your bank's Emergency Kill-Switch immediately via mobile app or call the 24/7 fraud hotline. "
                        f"Report unauthorized/induced transfer of {currency} {total_loss:,.2f} to {target_acc_str}. "
                        f"Demand immediate PayNow recall and request recipient bank account clawback."
                    ),
                    required_evidence=["PayNow / FAST Transaction Slip", "Bank Statement", "Caller Phone Number"],
                    statutory_reference="MAS Notice 644 on Technology Risk Management & MAS Shared Responsibility Framework (SRF)",
                ),
                ProceduralStep(
                    step_number=2,
                    stage="LAW_ENFORCEMENT_GD",
                    authority_name="Singapore Police Force (SPF) & Anti-Scam Centre (ASC)",
                    contact_channel="SPF E-Services (eservices.police.gov.sg) | Hotline: 1800 255 0000 / Anti-Scam Helpline 1800-722-6688",
                    timeline_window="Within 24 Hours",
                    instructions=(
                        f"File an official Police Report online via SPF E-Services. Detail communication with suspect {target_phone_str}. "
                        f"The Anti-Scam Centre (ASC) collaborates directly with 50+ financial institutions to initiate instant account freezing."
                    ),
                    required_evidence=["SPF Police Report Number", "Chat records", "Transfer slips", "ProofPath Case Dossier"],
                    statutory_reference="Corruption, Drug Trafficking and Other Serious Crimes (Confiscation of Benefits) Act (CDSA)",
                ),
                ProceduralStep(
                    step_number=3,
                    stage="COMMUNITY_DEFENSE",
                    authority_name="ScamShield (National Crime Prevention Council / GovTech)",
                    contact_channel="ScamShield App & Web Portal (scamshield.org.sg) | WhatsApp Bot: +65 8722 6688",
                    timeline_window="Within 48 Hours",
                    instructions=(
                        f"Submit suspect phone number {target_phone_str} and associated domains/messages to ScamShield to "
                        f"ensure nationwide network-level blocking by telcos (Singtel, StarHub, M1)."
                    ),
                    required_evidence=["Suspect phone number", "Scam message screenshots", "Phishing URLs"],
                    statutory_reference="Infocomm Media Development Authority (IMDA) Anti-Spoofing Guidelines",
                ),
                ProceduralStep(
                    step_number=4,
                    stage="REGULATOR_ESCALATION",
                    authority_name="Financial Industry Disputes Resolution Centre (FIDReC) / MAS",
                    contact_channel="FIDReC Portal (fidrec.com.sg) | MAS Consumer Advisory",
                    timeline_window="Day 14 - Month 6",
                    instructions=(
                        f"If the originating bank refuses restitution under the MAS Shared Responsibility Framework (SRF), "
                        f"file a formal dispute with FIDReC for binding adjudication up to SGD 100,000."
                    ),
                    required_evidence=["Final Bank Rejection Letter", "SPF Police Report", "ProofPath Evidence Package"],
                    statutory_reference="Monetary Authority of Singapore (MAS) Shared Responsibility Framework (SRF) 2024",
                ),
            ]

        else:
            # General / International Jurisdiction
            return [
                ProceduralStep(
                    step_number=1,
                    stage="IMMEDIATE_FREEZE",
                    authority_name="Financial Institution Anti-Fraud Department",
                    contact_channel="Issuing Bank Fraud Hotline",
                    timeline_window="0 - 2 Hours",
                    instructions=f"Contact issuing bank to recall transaction {txn_str} totaling {currency} {total_loss:,.2f}.",
                    required_evidence=["Transaction Receipt", "Payment Confirmation"],
                    statutory_reference="International Banking Wire Recall Protocols (SWIFT MT192 / Regional Clearing)",
                ),
                ProceduralStep(
                    step_number=2,
                    stage="LAW_ENFORCEMENT_GD",
                    authority_name="National Cyber Crime Reporting Agency",
                    contact_channel="National Police Cyber Bureau",
                    timeline_window="Within 24 Hours",
                    instructions=f"Lodge cyber fraud complaint against suspect {target_phone_str} with full forensic evidence.",
                    required_evidence=["ProofPath Dossier", "Evidence Artifacts"],
                    statutory_reference="Computer Misuse & Cybercrime Legislation",
                ),
            ]

    def generate_complaint_drafts(
        self,
        jurisdiction: Jurisdiction,
        case_id: str,
        victim_name: str,
        victim_contact: str,
        evidence_items: List[EvidenceItem],
        risk_assessment: RiskAssessment,
        total_loss: float,
        currency: str,
    ) -> List[ComplaintDraft]:
        """Generate ready-to-file complaint letters for financial providers and law enforcement."""
        # Collate suspect details
        suspect_phones = []
        suspect_accounts = []
        txn_ids = []
        for it in evidence_items:
            for ent in it.extracted_entities:
                if ent.role == "suspect" and ent.entity_type == "phone_number":
                    suspect_phones.append(ent.normalized_value or ent.value)
            for tx in it.extracted_transactions:
                if tx.recipient_account:
                    suspect_accounts.append(f"{tx.recipient_account} ({tx.payment_method or 'Transfer'})")
                if tx.transaction_id:
                    txn_ids.append(tx.transaction_id)

        phone_text = ", ".join(list(set(suspect_phones))) or "Unidentified caller"
        acc_text = ", ".join(list(set(suspect_accounts))) or phone_text
        txn_text = ", ".join(list(set(txn_ids))) or "Transaction referenced in exhibits"
        exhibits = [it.filename for it in evidence_items]

        drafts: List[ComplaintDraft] = []

        if jurisdiction == Jurisdiction.BANGLADESH:
            # 1. Bank/MFS Provider Complaint
            mfs_draft = (
                f"Date: Immediate Lodgement\n"
                f"To: The Head of Fraud Management & Customer Dispute Desk\n"
                f"Mobile Financial Services / Commercial Bank Provider\n"
                f"Subject: URGENT: Disputed Fraudulent Transaction Settlement & Immediate Account Freeze Request (Case ID: {case_id})\n\n"
                f"Dear Sir/Madam,\n\n"
                f"I am writing to formally lodge an emergency complaint regarding an unauthorized/fraudulently induced financial transaction. "
                f"Under false pretenses and coercive tactics ({risk_assessment.primary_scam_pattern}), funds were fraudulently extracted from my account.\n\n"
                f"INCIDENT SUMMARY:\n"
                f"- Complainant: {victim_name} ({victim_contact})\n"
                f"- Fraudulent Inducement Source: Phone Number(s) {phone_text}\n"
                f"- Destination Recipient Account(s): {acc_text}\n"
                f"- Disputed Transaction ID(s): {txn_text}\n"
                f"- Total Defrauded Sum: {currency} {total_loss:,.2f}\n"
                f"- Detected Forensic Red Flags: {', '.join(risk_assessment.tactics_detected[:3])}\n\n"
                f"STATUTORY DEMAND:\n"
                f"Pursuant to Bangladesh Bank PSD Circular No. 06/2018 regarding Fraud and Dispute Settlement, I demand that you immediately place "
                f"a temporary freeze / hold on destination account {acc_text} to prevent cash-out of the defrauded proceeds, and provide me with an official "
                f"dispute ticket reference within 24 hours.\n\n"
                f"All supporting multimodal evidence, message logs, and transaction receipts are indexed in attached Exhibits A through {chr(65 + max(0, len(exhibits)-1))}.\n\n"
                f"Respectfully submitted,\n"
                f"{victim_name}\n"
                f"Contact: {victim_contact}\n"
            )
            drafts.append(
                ComplaintDraft(
                    target_authority="MFS / Bank Fraud Investigation Desk",
                    jurisdiction="BANGLADESH",
                    subject=f"URGENT: Disputed Transaction Reversal & Account Freeze (Case ID: {case_id})",
                    body=mfs_draft,
                    exhibits_referenced=exhibits,
                )
            )

            # 2. Police General Diary (GD) / CID Cyber Police Application
            police_draft = (
                f"To: The Officer-in-Charge\n"
                f"Police Station (Thana) / Cyber Crime Investigation Division, CID\n"
                f"Subject: Prayer for Lodgement of General Diary (GD) & Cyber Crime Investigation under Cyber Security Act 2023\n\n"
                f"Sir,\n\n"
                f"I, {victim_name}, resident of Bangladesh (Contact: {victim_contact}), beg to inform you that I have become the victim "
                f"of an organized cyber financial fraud syndicate on the following grounds:\n\n"
                f"1. On the referenced date, unknown fraudster(s) operating mobile phone number(s) {phone_text} contacted me employing "
                f"deceptive techniques ({risk_assessment.primary_scam_pattern}).\n"
                f"2. Coerced by calculated psychological pressure and deception, financial transfers amounting to {currency} {total_loss:,.2f} "
                f"were executed to MFS/bank wallet {acc_text} under Transaction Reference(s) {txn_text}.\n"
                f"3. Forensic analysis demonstrates intentional deception with an assessed risk index of {risk_assessment.risk_score:.0f}/100 "
                f"and clear badge of criminal conspiracy.\n\n"
                f"I pray that you kindly register this General Diary (GD), initiate technical surveillance to track the biometric registration of "
                f"{phone_text}, and instruct the concerned financial gateway to freeze the ill-gotten funds.\n\n"
                f"Attached: ProofPath Comprehensive Forensic Evidence Dossier & Exhibits ({', '.join(exhibits)}).\n\n"
                f"Yours faithfully,\n"
                f"{victim_name}\n"
            )
            drafts.append(
                ComplaintDraft(
                    target_authority="Bangladesh Police / CID Cyber Crime Division",
                    jurisdiction="BANGLADESH",
                    subject="Prayer for Registration of General Diary (GD) - Financial Cyber Fraud",
                    body=police_draft,
                    exhibits_referenced=exhibits,
                )
            )

        elif jurisdiction == Jurisdiction.SINGAPORE:
            # 1. Singapore Police Force (SPF) / Anti-Scam Centre (ASC) Police Report Draft
            spf_draft = (
                f"SINGAPORE POLICE FORCE - FORMAL REPORT DETAILS\n"
                f"To: Officer-in-Charge, Anti-Scam Centre (ASC) / Police Division\n"
                f"Reference Case ID: {case_id}\n\n"
                f"COMPLAINANT PARTICULARS:\n"
                f"- Name: {victim_name}\n"
                f"- Contact: {victim_contact}\n\n"
                f"DETAILS OF INCIDENT:\n"
                f"- Scam Typology: {risk_assessment.primary_scam_pattern}\n"
                f"- Suspect Communication Lines: {phone_text}\n"
                f"- Destination Account / PayNow Proxy: {acc_text}\n"
                f"- Payment Transaction Reference(s): {txn_text}\n"
                f"- Total Financial Loss: {currency} {total_loss:,.2f}\n"
                f"- Assessed Threat Level: {risk_assessment.risk_level} ({risk_assessment.risk_score:.0f}/100)\n\n"
                f"NARRATIVE OF OFFENCE:\n"
                f"The complainant was approached via digital messaging and coerced through {', '.join(risk_assessment.tactics_detected)} into "
                f"authorizing funds transfer. The complainant subsequently confirmed the representations were entirely fraudulent.\n\n"
                f"RELIEF SOUGHT:\n"
                f"Urgent intervention by the Anti-Scam Centre under the CDSA to coordinate inter-bank clawback with the recipient financial "
                f"institution and institute telecommunication blacklisting via ScamShield.\n\n"
                f"Exhibits Indexed: {', '.join(exhibits)}\n"
            )
            drafts.append(
                ComplaintDraft(
                    target_authority="Singapore Police Force (SPF) & Anti-Scam Centre",
                    jurisdiction="SINGAPORE",
                    subject=f"SPF Anti-Scam Report Draft - Financial Loss SGD {total_loss:,.2f} (Case: {case_id})",
                    body=spf_draft,
                    exhibits_referenced=exhibits,
                )
            )

            # 2. Bank Dispute & FIDReC Notice
            bank_sg_draft = (
                f"To: Fraud Risk Operations & Dispute Resolution Unit\n"
                f"Issuing Bank (Singapore)\n"
                f"Subject: FORMAL FRAUD DISPUTE & RESTITUTION CLAIM - MAS SRF (Case ID: {case_id})\n\n"
                f"Dear Dispute Team,\n\n"
                f"I hereby lodge an expedited dispute claim for fraudulent transactions totaling {currency} {total_loss:,.2f} "
                f"effected via PayNow / FAST under Reference(s): {txn_text}.\n\n"
                f"Pursuant to the MAS Shared Responsibility Framework (SRF) and Guidelines on Technology Risk Management (Notice 644), "
                f"I request that your fraud department confirm:\n"
                f"1. Whether real-time transaction monitoring flagged the abnormal velocity to new payee {acc_text}.\n"
                f"2. Whether an immediate fund recall request was transmitted to the receiving financial institution.\n"
                f"3. A formal resolution letter within 21 days for submission to FIDReC if reimbursement is declined.\n\n"
                f"Complainant: {victim_name} ({victim_contact})\n"
                f"Supporting Evidence Attached: {', '.join(exhibits)}\n"
            )
            drafts.append(
                ComplaintDraft(
                    target_authority="Bank Fraud Dispute Unit / FIDReC",
                    jurisdiction="SINGAPORE",
                    subject=f"Expedited Fraud Dispute under MAS Framework - {txn_text}",
                    body=bank_sg_draft,
                    exhibits_referenced=exhibits,
                )
            )

        else:
            # General / International Jurisdiction Complaint Drafts
            intl_bank_draft = (
                f"To: Fraud Operations & Wire Recall Department\n"
                f"Originating Financial Gateway / Commercial Bank\n"
                f"Subject: EMERGENCY WIRE RECALL & FRAUD HOLD REQUEST - Reference Case: {case_id}\n\n"
                f"Dear Fraud Investigation Unit,\n\n"
                f"I am submitting an urgent fraud dispute regarding unauthorized/fraudulently induced financial transactions totaling "
                f"{currency} {total_loss:,.2f}.\n\n"
                f"INCIDENT PARTICULARS:\n"
                f"- Complainant: {victim_name} ({victim_contact})\n"
                f"- Fraud Typology: {risk_assessment.primary_scam_pattern}\n"
                f"- Beneficiary / Recipient Coordinates: {acc_text}\n"
                f"- Disputed Transaction Reference(s): {txn_text}\n"
                f"- Suspect Line(s): {phone_text}\n\n"
                f"EMERGENCY REQUEST:\n"
                f"Under international inter-bank fraud recall protocols (SWIFT MT192 / Regional Clearing Settlement), "
                f"please transmit an immediate payment recall message to the beneficiary institution to freeze and repatriate the disputed funds.\n\n"
                f"Forensic exhibits and SHA-256 evidence manifest attached ({', '.join(exhibits)}).\n\n"
                f"Sincerely,\n"
                f"{victim_name}\n"
            )
            drafts.append(
                ComplaintDraft(
                    target_authority="Bank Fraud Operations / Wire Recall Desk",
                    jurisdiction="GENERAL",
                    subject=f"URGENT: Fraud Wire Recall & Account Freeze (Case: {case_id})",
                    body=intl_bank_draft,
                    exhibits_referenced=exhibits,
                )
            )

            intl_cyber_draft = (
                f"To: National Cyber Crime Investigation Division / Financial Crimes Bureau\n"
                f"Subject: Formal Cyber Financial Fraud Incident Report (Case Reference: {case_id})\n\n"
                f"Complainant Particulars: {victim_name} ({victim_contact})\n\n"
                f"STATEMENT OF FACTS:\n"
                f"1. The complainant was targeted by organized cyber financial fraudsters utilizing deceptive techniques "
                f"({risk_assessment.primary_scam_pattern}).\n"
                f"2. Induced by coercive tactics ({', '.join(risk_assessment.tactics_detected)}), funds amounting to {currency} {total_loss:,.2f} "
                f"were transferred to recipient account/wallet {acc_text} under reference(s) {txn_text}.\n"
                f"3. Forensic assessment indicates an elevated risk index of {risk_assessment.risk_score:.0f}/100 with documented digital indicators.\n\n"
                f"PRAYER FOR RELIEF:\n"
                f"Lodge this formal crime report, initiate tracing of suspect communication infrastructure ({phone_text}), and coordinate "
                f"with relevant financial monitoring units for recovery.\n\n"
                f"Exhibits Indexed: {', '.join(exhibits)}\n\n"
                f"Submitted by,\n"
                f"{victim_name}\n"
            )
            drafts.append(
                ComplaintDraft(
                    target_authority="National Cyber Crime Reporting Agency",
                    jurisdiction="GENERAL",
                    subject=f"Official Cyber Fraud Complaint - Loss {currency} {total_loss:,.2f} (Case: {case_id})",
                    body=intl_cyber_draft,
                    exhibits_referenced=exhibits,
                )
            )

        return drafts
