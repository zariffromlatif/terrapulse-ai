"""Verification and Risk Engine: Cross-document checks, timestamp chronology checks, and deterministic rules."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from proofpath.models import (
    ChronologicalEvent,
    Contradiction,
    EvidenceItem,
    EvidenceType,
    RiskAssessment,
)


class VerificationEngine:
    """Verifies evidence consistency, validates chronology, and calculates risk scores."""

    def __init__(self):
        # Heuristic keywords for tactics
        self.urgency_keywords = [
            "immediate", "immediately", "within 30 min", "urgent", "arrest",
            "freeze your account", "account suspended", "police case", "jail",
            "terminate immediately", "last warning", "final notice"
        ]
        self.task_job_keywords = [
            "earn daily", "telegram task", "click product", "commission rebate",
            "deposit to unlock", "vip level", "daily salary", "part-time job",
            "review products", "crypto task"
        ]
        self.customs_lottery_keywords = [
            "parcel held", "customs clearance", "airport tax", "diplomatic courier",
            "lottery winner", "congratulations won", "claim prize fee", "delivery charge"
        ]
        self.otp_phishing_keywords = [
            "share otp", "send 6-digit", "bKash pin", "pin number", "verification code",
            "confirm otp", "bank otp", "passcode"
        ]
        self.impersonation_keywords = [
            "bangladesh bank", "police officer", "cid", "singapore police force",
            "anti-scam centre", "monetary authority of singapore", "mas officer",
            "high court", "dbs security officer", "bkash head office", "customs officer"
        ]

    def verify_case(self, evidence_items: List[EvidenceItem]) -> Tuple[RiskAssessment, List[ChronologicalEvent]]:
        """Run all verification passes across evidence items and construct chronological timeline."""
        contradictions: List[Contradiction] = []
        red_flags: List[str] = []
        tactics_detected: List[str] = []

        all_text = " ".join([item.raw_text or item.summary for item in evidence_items]).lower()

        # 1. Tactic detection
        if any(w in all_text for w in self.urgency_keywords):
            tactics_detected.append("Urgency & Coercive Pressure")
            red_flags.append("Suspect created artificial urgency with threats of immediate penalty/arrest.")

        if any(w in all_text for w in self.task_job_keywords):
            tactics_detected.append("High-Yield Task / Affiliate Rebate Lure")
            red_flags.append("Suspect promised high daily returns or task rebates requiring upfront capital deposits.")

        if any(w in all_text for w in self.customs_lottery_keywords):
            tactics_detected.append("Advance-Fee / Parcel Clearance Fee")
            red_flags.append("Suspect demanded upfront clearance fees for a fabricated high-value parcel or prize.")

        if any(w in all_text for w in self.otp_phishing_keywords):
            tactics_detected.append("Credential / OTP Solicitation")
            red_flags.append("Suspect solicited sensitive one-time passwords (OTP) or security PINs.")

        if any(w in all_text for w in self.impersonation_keywords):
            tactics_detected.append("Institutional Authority Impersonation")
            red_flags.append("Suspect falsely represented law enforcement, central banks, or financial institutions.")

        # 2. Cross-document checks
        receipt_items = [it for it in evidence_items if it.evidence_type == EvidenceType.TRANSACTION_RECEIPT]
        chat_items = [it for it in evidence_items if it.evidence_type in (EvidenceType.CHAT_MESSAGE, EvidenceType.VOICE_NOTE, EvidenceType.CONTRACT_DOCUMENT)]

        # Check: Identity disguise (impersonating authority while receiving funds to personal wallet/account)
        def add_contradiction(c: Contradiction):
            for existing in contradictions:
                if (
                    existing.rule_id == c.rule_id
                    and existing.evidence_item_a == c.evidence_item_a
                    and existing.evidence_item_b == c.evidence_item_b
                ):
                    return
            contradictions.append(c)

        # Check: Identity disguise (impersonating authority while receiving funds to personal wallet/account)
        if "Institutional Authority Impersonation" in tactics_detected and receipt_items:
            for r_item in receipt_items:
                for tx in r_item.extracted_transactions:
                    if tx.recipient_account and not tx.recipient_account.lower().startswith("corp"):
                        add_contradiction(
                            Contradiction(
                                rule_id="RULE_IMPERSONATION_PERSONAL_P2P",
                                severity="HIGH",
                                title="Institutional Claim vs. Personal P2P Recipient Contradiction",
                                description=(
                                    f"Suspect communications claimed representation of an official regulatory/financial institution, "
                                    f"yet transaction was directed to personal transfer account ({tx.recipient_account} via {tx.payment_method}). "
                                    f"Official institutions never collect funds into individual personal accounts."
                                ),
                                evidence_item_a=r_item.filename,
                                conflicting_fields={
                                    "claimed_entity": "Government / Bank Institution",
                                    "actual_recipient": tx.recipient_account,
                                    "channel": tx.payment_method,
                                },
                            )
                        )

        # Check: Amount mismatch between chat promise/request and receipt
        if chat_items and receipt_items:
            for c_item in chat_items:
                c_text = c_item.raw_text or ""
                # Strip out known timestamps to prevent year numbers (e.g. 2026) from being treated as amounts
                clean_chat_text = c_text
                for ts_raw in c_item.timestamps_found:
                    clean_chat_text = clean_chat_text.replace(ts_raw, " ")
                # Strip 4-digit years from remaining text
                clean_chat_text = re.sub(r"\b20[2-3][0-9]\b", " ", clean_chat_text)

                # Extract numbers that have financial/currency indicators or amount keywords
                explicit_amt_matches = re.findall(
                    r"(?:BDT|TK|৳|SGD|\$|USD|EUR|USDT|Amount|Fee|Charge|Deposit|Pay|Transfer|Send)\s*[:\s]?\s*([0-9]{1,3}(?:,[0-9]{3})+|[0-9]{2,7})(?:\.[0-9]{1,2})?",
                    clean_chat_text,
                    re.IGNORECASE,
                )
                reverse_amt_matches = re.findall(
                    r"([0-9]{1,3}(?:,[0-9]{3})+|[0-9]{2,7})(?:\.[0-9]{1,2})?\s*(?:BDT|TK|৳|SGD|USD|dollars|taka)",
                    clean_chat_text,
                    re.IGNORECASE,
                )

                chat_numbers: List[float] = []
                for m in explicit_amt_matches + reverse_amt_matches:
                    try:
                        chat_numbers.append(float(m.replace(",", "")))
                    except ValueError:
                        continue

                # If no currency-anchored amount found, check if chat mentions standalone numbers only when fee/pay words exist
                if not chat_numbers and any(w in clean_chat_text.lower() for w in ["pay", "deposit", "fee", "transfer", "charge", "sum"]):
                    general_numbers = [float(n.replace(",", "")) for n in re.findall(r"\b[1-9]\d{2,6}\b", clean_chat_text)]
                    # Exclude numbers that look like phone numbers or timestamps
                    chat_numbers = [gn for gn in general_numbers if gn not in (2024.0, 2025.0, 2026.0, 2027.0)]

                for r_item in receipt_items:
                    for tx in r_item.extracted_transactions:
                        if tx.amount and tx.amount > 0 and chat_numbers:
                            # If chat mentions amounts, check if any matches within tolerance
                            if not any(abs(cn - tx.amount) < 1.0 for cn in chat_numbers):
                                add_contradiction(
                                    Contradiction(
                                        rule_id="RULE_AMOUNT_INCONSISTENCY",
                                        severity="MEDIUM",
                                        title="Chat Solicited Amount vs. Incurred Transaction Mismatch",
                                        description=(
                                            f"Transaction receipt '{r_item.filename}' shows payment of {tx.currency} {tx.amount:,.2f}, "
                                            f"which deviates from amounts explicitly referenced in chat record '{c_item.filename}'. "
                                            f"Indicates hidden escalation fees or coercive demand escalation."
                                        ),
                                        evidence_item_a=r_item.filename,
                                        evidence_item_b=c_item.filename,
                                        conflicting_fields={
                                            "receipt_amount": tx.amount,
                                            "chat_candidate_amounts": chat_numbers[:3],
                                        },
                                    )
                                )

        # 3. Timestamp chronology checks & Timeline construction
        parsed_timestamps: List[Tuple[Optional[datetime], str, EvidenceItem]] = []

        for item in evidence_items:
            for ts_str in item.timestamps_found:
                dt = self._parse_timestamp(ts_str)
                parsed_timestamps.append((dt, ts_str, item))

        # Detect backdated receipts or temporal anomalies
        chat_dts = [p[0] for p in parsed_timestamps if p[2].evidence_type == EvidenceType.CHAT_MESSAGE and p[0]]
        receipt_dts = [p[0] for p in parsed_timestamps if p[2].evidence_type == EvidenceType.TRANSACTION_RECEIPT and p[0]]

        if chat_dts and receipt_dts:
            earliest_chat = min(chat_dts)
            earliest_receipt = min(receipt_dts)
            if earliest_receipt < earliest_chat:
                add_contradiction(
                    Contradiction(
                        rule_id="RULE_TEMPORAL_ANOMALY_BACKDATED",
                        severity="HIGH",
                        title="Chronological Conflict: Receipt Predates Contact Initiation",
                        description=(
                            f"Payment receipt indicates timestamp {earliest_receipt.isoformat()} preceding the first communication "
                            f"timestamp {earliest_chat.isoformat()}. Suggests either forged receipt metadata or inaccurate evidence logging."
                        ),
                        evidence_item_a=receipt_items[0].filename if receipt_items else "receipt",
                        evidence_item_b=chat_items[0].filename if chat_items else "chat",
                        conflicting_fields={
                            "receipt_time": earliest_receipt.isoformat(),
                            "chat_start_time": earliest_chat.isoformat(),
                        },
                    )
                )

        # Build clean chronological narrative sorted strictly by parsed timestamp
        raw_events: List[Tuple[Optional[datetime], Dict[str, Any]]] = []

        # Add communication and non-receipt events
        non_receipt_items = [it for it in evidence_items if it.evidence_type != EvidenceType.TRANSACTION_RECEIPT]
        for item in non_receipt_items:
            ts_str = item.timestamps_found[0] if item.timestamps_found else None
            dt = self._parse_timestamp(ts_str) if ts_str else None

            # Determine specific event type based on item category
            if item.evidence_type == EvidenceType.VOICE_NOTE:
                ev_type = "VOICE_INTERACTION"
            elif item.evidence_type == EvidenceType.PHISHING_PAGE:
                ev_type = "MALICIOUS_LINK_EXPOSURE"
            elif item.evidence_type == EvidenceType.CONTRACT_DOCUMENT:
                ev_type = "CONTRACT_ISSUANCE"
            else:
                ev_type = "SUSPECT_COMMUNICATION"

            raw_events.append((
                dt,
                {
                    "timestamp": ts_str,
                    "event_type": ev_type,
                    "description": f"Suspect contact via {item.evidence_type.value} document '{item.filename}'. Summary: {item.summary}",
                    "evidence_sources": [item.filename],
                    "actors": [e.value for e in item.extracted_entities if e.role == "suspect"][:3],
                    "amount": None,
                    "currency": None,
                }
            ))

        # Add payment execution events
        for item in receipt_items:
            for tx in item.extracted_transactions:
                tx_ts = tx.timestamp or (item.timestamps_found[0] if item.timestamps_found else None)
                dt = self._parse_timestamp(tx_ts) if tx_ts else None

                raw_events.append((
                    dt,
                    {
                        "timestamp": tx_ts,
                        "event_type": "PAYMENT_EXECUTION",
                        "description": (
                            f"Victim transferred {tx.currency} {tx.amount or 0.0:,.2f} via {tx.payment_method or 'payment transfer'} "
                            f"(TxID: {tx.transaction_id or 'N/A'}) to suspect account {tx.recipient_account or 'Unspecified'}."
                        ),
                        "evidence_sources": [item.filename],
                        "actors": [tx.recipient_account or "Suspect Account"],
                        "amount": tx.amount,
                        "currency": tx.currency,
                    }
                ))

        # Sort raw events chronologically: events with parsed datetimes first in ascending order, then un-timestamped
        raw_events.sort(key=lambda x: (x[0] is None, x[0] or datetime.max))

        chronology: List[ChronologicalEvent] = []
        comm_seen = False
        for seq, (dt, ev_dict) in enumerate(raw_events, start=1):
            etype = ev_dict["event_type"]
            # Mark the very first communication as INITIAL_COMMUNICATION
            if etype in ("SUSPECT_COMMUNICATION", "VOICE_INTERACTION"):
                if not comm_seen:
                    etype = "INITIAL_COMMUNICATION"
                    comm_seen = True
                else:
                    etype = "FOLLOWUP_COMMUNICATION"

            chronology.append(
                ChronologicalEvent(
                    sequence_number=seq,
                    timestamp=ev_dict["timestamp"],
                    event_type=etype,
                    description=ev_dict["description"],
                    evidence_sources=ev_dict["evidence_sources"],
                    actors=ev_dict["actors"],
                    amount=ev_dict["amount"],
                    currency=ev_dict["currency"],
                )
            )

        # Fallback if chronology was empty
        if not chronology:
            for idx, it in enumerate(evidence_items, start=1):
                chronology.append(
                    ChronologicalEvent(
                        sequence_number=idx,
                        timestamp=it.timestamps_found[0] if it.timestamps_found else None,
                        event_type="EVIDENCE_RECORD",
                        description=f"Evidence artifact '{it.filename}' submitted and verified. {it.summary}",
                        evidence_sources=[it.filename],
                    )
                )

        # 4. Primary scam pattern determination
        primary_pattern = "Unclassified Financial Fraud"
        secondary_patterns: List[str] = []

        if "Institutional Authority Impersonation" in tactics_detected:
            primary_pattern = "Institutional Authority Impersonation & Extortion"
            if "Urgency & Coercive Pressure" in tactics_detected:
                secondary_patterns.append("Coercive Account-Freezing Hoax")
        elif "High-Yield Task / Affiliate Rebate Lure" in tactics_detected:
            primary_pattern = "High-Yield Affiliate / Task Investment Scam"
        elif "Credential / OTP Solicitation" in tactics_detected:
            primary_pattern = "Account Takeover via OTP Phishing"
        elif "Advance-Fee / Parcel Clearance Fee" in tactics_detected:
            primary_pattern = "Advance-Fee Parcel & Customs Fee Fraud"
        else:
            if receipt_items:
                primary_pattern = "Unauthorized Remote Payment Coercion"

        # 5. Risk score calculation
        score = 25.0  # Base score for any reported incident
        if tactics_detected:
            score += len(tactics_detected) * 15.0
        if contradictions:
            for c in contradictions:
                if c.severity == "HIGH":
                    score += 20.0
                else:
                    score += 10.0
        if receipt_items:
            score += 15.0

        # Cap score between 0 and 100
        score = min(max(score, 10.0), 100.0)

        risk_level = "LOW"
        if score >= 80:
            risk_level = "CRITICAL"
        elif score >= 60:
            risk_level = "HIGH"
        elif score >= 35:
            risk_level = "MEDIUM"

        assessment = RiskAssessment(
            risk_score=score,
            risk_level=risk_level,
            primary_scam_pattern=primary_pattern,
            secondary_patterns=secondary_patterns,
            tactics_detected=tactics_detected,
            contradictions=contradictions,
            red_flags=red_flags,
        )

        return assessment, chronology

    def _parse_timestamp(self, ts_str: str) -> Optional[datetime]:
        """Try multiple datetime formats to parse raw timestamp string with AM/PM and timezone support."""
        clean_str = ts_str.strip()
        # Try native ISO parse first
        try:
            iso_candidate = clean_str.replace("Z", "+00:00")
            return datetime.fromisoformat(iso_candidate)
        except Exception:
            pass

        # Strip common trailing timezones before strptime
        clean_str = re.sub(r"\s+(?:SGT|BDT|UTC|GMT|EST|EDT|PST|PDT|CST|CDT)\b", "", clean_str, flags=re.IGNORECASE).strip()

        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%d",
            "%Y-%m-%d %I:%M:%S %p",
            "%Y-%m-%d %I:%M %p",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y %H:%M",
            "%d/%m/%Y",
            "%d/%m/%Y %I:%M:%S %p",
            "%d/%m/%Y %I:%M %p",
            "%d-%m-%Y %H:%M:%S",
            "%d-%m-%Y %H:%M",
            "%d-%m-%Y",
            "%d-%m-%Y %I:%M:%S %p",
            "%d-%m-%Y %I:%M %p",
            "%d %b %Y %H:%M:%S",
            "%d %b %Y %H:%M",
            "%d %b %Y",
            "%d-%b-%Y %H:%M:%S",
            "%d-%b-%Y %H:%M",
            "%d-%b-%Y",
            "%d %B %Y %H:%M:%S",
            "%d %B %Y %H:%M",
            "%d %B %Y",
            "%d-%B-%Y %H:%M:%S",
            "%d-%B-%Y %H:%M",
            "%d-%B-%Y",
            "%b %d, %Y %H:%M:%S",
            "%b %d, %Y %H:%M",
            "%b %d, %Y",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(clean_str, fmt)
            except ValueError:
                continue
        return None
