"""Multimodal evidence extraction engine using Google GenAI SDK with fallback deterministic parsing."""

from __future__ import annotations

import hashlib
import io
import json
import os
import re
from typing import Any, Dict, List, Optional
from proofpath.models import (
    Currency,
    EvidenceItem,
    EvidenceType,
    ExtractedEntity,
    ExtractedTransaction,
)


def resolve_mime_type(filename: str, mime_type: Optional[str] = None) -> str:
    """Infer accurate MIME type from filename extension or provide verified default."""
    if mime_type and mime_type.strip() not in ("application/octet-stream", "binary/octet-stream", ""):
        return mime_type.strip()
    ext = os.path.splitext(filename)[1].lower()
    ext_map = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".pdf": "application/pdf",
        ".txt": "text/plain",
        ".json": "application/json",
        ".csv": "text/csv",
        ".mp3": "audio/mp3",
        ".wav": "audio/wav",
        ".m4a": "audio/m4a",
        ".ogg": "audio/ogg",
        ".aac": "audio/aac",
        ".html": "text/html",
    }
    return ext_map.get(ext, "application/octet-stream")


class EvidenceExtractor:
    """Extracts structured entities, transactions, and facts from multimodal evidence."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self._client = None
        if self.api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except Exception:
                self._client = None

    def process_file_content(
        self,
        filename: str,
        content_bytes: bytes,
        mime_type: Optional[str] = None,
        override_type: Optional[EvidenceType] = None,
    ) -> EvidenceItem:
        """Process binary or text content into a structured EvidenceItem."""
        item_id = hashlib.sha256((filename + str(len(content_bytes))).encode()).hexdigest()[:12]
        sha256_hash = hashlib.sha256(content_bytes).hexdigest()
        resolved_mime = resolve_mime_type(filename, mime_type)

        # Determine if content is text or binary
        is_text = False
        text_content = ""

        # Check for PDF document text extraction
        if resolved_mime == "application/pdf" or filename.lower().endswith(".pdf") or content_bytes.startswith(b"%PDF-"):
            try:
                import pypdf
                reader = pypdf.PdfReader(io.BytesIO(content_bytes))
                pages_text = [p.extract_text() or "" for p in reader.pages]
                extracted_pdf_text = "\n".join(pages_text).strip()
                if extracted_pdf_text:
                    text_content = extracted_pdf_text
                    is_text = True
            except Exception:
                pass

        if not text_content:
            try:
                text_content = content_bytes.decode("utf-8")
                is_text = True
            except UnicodeDecodeError:
                try:
                    text_content = content_bytes.decode("latin-1")
                    # Check for printable ratio
                    printable = sum(1 for c in text_content if c.isprintable())
                    if printable / max(len(text_content), 1) > 0.85:
                        is_text = True
                    else:
                        text_content = ""
                except Exception:
                    text_content = ""

        # Attempt Gemini multimodal extraction if client is available
        if self._client:
            try:
                gemini_result = self._extract_with_gemini(
                    filename=filename,
                    content_bytes=content_bytes,
                    is_text=is_text,
                    text_content=text_content,
                    mime_type=resolved_mime,
                )
                if gemini_result:
                    gemini_result.item_id = item_id
                    gemini_result.filename = filename
                    gemini_result.sha256_hash = sha256_hash
                    gemini_result.file_type = resolved_mime
                    if override_type:
                        gemini_result.evidence_type = override_type
                    return gemini_result
            except Exception:
                # Fallback to local parsing on any API failure
                pass

        # Deterministic extraction fallback
        return self._extract_deterministic(
            item_id=item_id,
            filename=filename,
            sha256_hash=sha256_hash,
            content_bytes=content_bytes,
            text_content=text_content,
            override_type=override_type,
            detected_mime=resolved_mime,
        )

    def _extract_with_gemini(
        self,
        filename: str,
        content_bytes: bytes,
        is_text: bool,
        text_content: str,
        mime_type: Optional[str],
    ) -> Optional[EvidenceItem]:
        """Call Google GenAI SDK for multimodal extraction."""
        if not self._client:
            return None

        prompt = (
            "You are an expert digital forensics investigator analyzing financial fraud evidence. "
            "Examine this evidence carefully. Extract all structured facts including: "
            "1. Evidence type (TRANSACTION_RECEIPT, CHAT_MESSAGE, VOICE_NOTE, CALL_LOG, EMAIL, PHISHING_PAGE, CONTRACT_DOCUMENT, OTHER). "
            "2. Concise factual summary of what this document shows. "
            "3. All timestamps mentioned. "
            "4. Extracted entities (phone numbers, wallet accounts, bank accounts, domains, suspect names, platform names). "
            "5. All financial transactions (transaction ID, amount, currency, timestamp, sender, sender account, recipient, recipient account, payment method, reference note). "
            "Output strictly valid JSON conforming to this structure:\n"
            "{\n"
            '  "evidence_type": "TRANSACTION_RECEIPT",\n'
            '  "summary": "...",\n'
            '  "timestamps": ["2026-10-12T14:30:00"],\n'
            '  "entities": [{"entity_type": "phone_number", "value": "01712345678", "normalized_value": "+8801712345678", "role": "suspect", "confidence": 0.95}],\n'
            '  "transactions": [{"transaction_id": "TXN123", "amount": 25000.0, "currency": "BDT", "timestamp": "...", "sender": "...", "sender_account": "...", "recipient": "...", "recipient_account": "...", "payment_method": "bKash", "reference_note": "...", "confidence": 0.95}],\n'
            '  "confidence": 0.92\n'
            "}"
        )

        try:
            from google.genai import types

            contents = []
            if is_text:
                contents.append(f"Filename: {filename}\nContent:\n{text_content[:8000]}")
                contents.append(prompt)
            else:
                mtype = mime_type or "image/png"
                contents.append(
                    types.Part.from_bytes(data=content_bytes, mime_type=mtype)
                )
                contents.append(prompt)

            response = self._client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1,
                ),
            )
            raw_json = response.text.strip()
            data = json.loads(raw_json)

            ev_type_str = data.get("evidence_type", "OTHER")
            try:
                ev_type = EvidenceType(ev_type_str)
            except ValueError:
                ev_type = EvidenceType.OTHER

            entities = []
            for ent in data.get("entities", []):
                entities.append(
                    ExtractedEntity(
                        entity_type=ent.get("entity_type", "unknown"),
                        value=str(ent.get("value", "")),
                        normalized_value=str(ent.get("normalized_value", ent.get("value", ""))),
                        role=ent.get("role", "suspect"),
                        confidence=float(ent.get("confidence", 0.9)),
                        source_file=filename,
                    )
                )

            transactions = []
            for tx in data.get("transactions", []):
                transactions.append(
                    ExtractedTransaction(
                        transaction_id=tx.get("transaction_id"),
                        amount=float(tx.get("amount")) if tx.get("amount") is not None else None,
                        currency=tx.get("currency", "BDT"),
                        timestamp=tx.get("timestamp"),
                        sender=tx.get("sender"),
                        sender_account=tx.get("sender_account"),
                        recipient=tx.get("recipient"),
                        recipient_account=tx.get("recipient_account"),
                        payment_method=tx.get("payment_method"),
                        reference_note=tx.get("reference_note"),
                        confidence=float(tx.get("confidence", 0.9)),
                        source_file=filename,
                    )
                )

            return EvidenceItem(
                item_id="",
                filename=filename,
                file_type=mime_type or "application/octet-stream",
                sha256_hash="",
                evidence_type=ev_type,
                raw_text=text_content[:2000] if text_content else None,
                extracted_entities=entities,
                extracted_transactions=transactions,
                timestamps_found=data.get("timestamps", []),
                summary=data.get("summary", f"Extracted facts from {filename}"),
                confidence=float(data.get("confidence", 0.9)),
            )
        except Exception:
            return None

    def _extract_deterministic(
        self,
        item_id: str,
        filename: str,
        sha256_hash: str,
        content_bytes: bytes,
        text_content: str,
        override_type: Optional[EvidenceType] = None,
        detected_mime: str = "application/octet-stream",
    ) -> EvidenceItem:
        """Deterministic regex and heuristic extraction fallback."""
        lower_name = filename.lower()

        # Handle empty content gracefully
        if not content_bytes:
            return EvidenceItem(
                item_id=item_id,
                filename=filename,
                file_type=detected_mime,
                sha256_hash=sha256_hash,
                evidence_type=override_type or EvidenceType.OTHER,
                raw_text=None,
                extracted_entities=[],
                extracted_transactions=[],
                timestamps_found=[],
                summary=f"Empty evidence file '{filename}' (0 bytes). No forensic artifacts found.",
                confidence=0.1,
                metadata={"source": "deterministic_fallback", "empty": True},
            )

        # If text content is empty (e.g. image binary or raw binary), synthesize minimal text description or attempt string extraction
        if not text_content:
            strings_found = re.findall(rb"[A-Za-z0-9_\-\.\:\/\@\+\s]{5,100}", content_bytes)
            text_content = " ".join([s.decode("ascii", errors="ignore") for s in strings_found[:50]])

        # 1. Determine Evidence Type
        ev_type = override_type or EvidenceType.OTHER
        if not override_type:
            if any(k in lower_name for k in ["voice", "audio", "call", "recording", "transcript"]):
                ev_type = EvidenceType.VOICE_NOTE
            elif any(k in lower_name for k in ["receipt", "slip", "payment", "cashout", "transfer", "voucher", "statement", "invoice"]) or any(re.search(rf"\b{k}\b", lower_name) for k in ["tran", "txn", "trx"]):
                ev_type = EvidenceType.TRANSACTION_RECEIPT
            elif any(k in lower_name for k in ["chat", "msg", "sms", "whatsapp", "telegram", "conversation", "threat", "notice", "text", "demand"]):
                ev_type = EvidenceType.CHAT_MESSAGE
            elif any(k in lower_name for k in ["contract", "agreement", "offer_letter", "employment", "letter"]):
                ev_type = EvidenceType.CONTRACT_DOCUMENT
            elif any(k in lower_name for k in ["phish", "domain", "link", "url", "fake"]):
                ev_type = EvidenceType.PHISHING_PAGE
            else:
                # Content based classification
                content_upper = text_content.upper()
                if any(k in content_upper for k in ["AUDIO TRANSCRIPT", "VOICE NOTE", "SPEAKER 1", "CALL RECORDING"]):
                    ev_type = EvidenceType.VOICE_NOTE
                elif any(k in content_upper for k in ["TRANSACTION ID", "TXN ID", "TRXID", "PAYNOW REFERENCE", "SENT MONEY TO", "CASH OUT"]):
                    ev_type = EvidenceType.TRANSACTION_RECEIPT
                elif any(k in content_upper for k in ["WHATSAPP", "TELEGRAM", "USER:", "ASSISTANT:", "CHAT", "CALLER:", "SUSPECT:", "OFFICER:", "I AM "]):
                    ev_type = EvidenceType.CHAT_MESSAGE

        # 2. Extract Entities
        entities: List[ExtractedEntity] = []

        # Phone numbers: BD (01[3-9]\d{8} or +8801[3-9]\d{8}) and SG (+65[689]\d{7} or [689]\d{7})
        bd_phones = re.findall(r"(?:\+8801|01)[3-9]\d{8}\b", text_content)
        for p in set(bd_phones):
            norm = p if p.startswith("+880") else "+880" + p.lstrip("0")
            role = "suspect"
            if "victim" in lower_name or "my_phone" in lower_name or "sender" in lower_name:
                role = "victim"
            entities.append(
                ExtractedEntity(
                    entity_type="phone_number",
                    value=p,
                    normalized_value=norm,
                    role=role,
                    confidence=0.95,
                    source_file=filename,
                )
            )

        # Ensure SG phone regex has leading non-digit assertion to prevent matching inside 11-digit BD numbers
        sg_phones = re.findall(r"(?<!\d)(?:\+65\s?)?[689]\d{7}\b", text_content)
        for p in set(sg_phones):
            clean_digits = re.sub(r"\D", "", p)
            if len(clean_digits) == 8:
                norm = f"+65{clean_digits}"
            elif len(clean_digits) == 10 and clean_digits.startswith("65"):
                norm = f"+{clean_digits}"
            else:
                norm = p
            entities.append(
                ExtractedEntity(
                    entity_type="phone_number",
                    value=p,
                    normalized_value=norm,
                    role="suspect",
                    confidence=0.92,
                    source_file=filename,
                )
            )

        # Domains and URLs
        domains = re.findall(r"(?:https?:\/\/)?([a-zA-Z0-9\-]+\.(?:com|org|net|info|xyz|top|live|app|site|vip|cc|tk|ml)[a-zA-Z0-9\-\.\/\?\=\_]*)", text_content, re.IGNORECASE)
        for dom in set(domains):
            clean_dom = dom.split("/")[0].lower()
            if not any(trusted in clean_dom for trusted in ["google.com", "github.com", "microsoft.com", "w3.org"]):
                entities.append(
                    ExtractedEntity(
                        entity_type="domain",
                        value=dom,
                        normalized_value=clean_dom,
                        role="suspect",
                        confidence=0.90,
                        source_file=filename,
                    )
                )

        # Telegram / WhatsApp handles
        telegram_handles = re.findall(r"(?:@|t\.me\/)([a-zA-Z0-9_]{5,32})", text_content)
        for h in set(telegram_handles):
            entities.append(
                ExtractedEntity(
                    entity_type="telegram_handle",
                    value=h,
                    normalized_value=f"@{h.lstrip('@')}",
                    role="suspect",
                    confidence=0.90,
                    source_file=filename,
                )
            )

        # 3. Extract Transactions
        transactions: List[ExtractedTransaction] = []

        # Find Transaction IDs
        trx_matches = re.findall(r"(?:TrxID|Txn ID|Transaction ID|Ref ID|Reference Number|UTR)[:\s]+([A-Za-z0-9]{8,24})", text_content, re.IGNORECASE)
        # Amounts
        amt_matches = re.findall(
            r"(?:BDT|TK|৳|SGD|\$|USD|Amount[:\s]+)\s?((?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{1,2})?)",
            text_content,
            re.IGNORECASE,
        )

        # Timestamps with AM/PM support and month names
        timestamp_matches = re.findall(
            r"\b(\d{4}-\d{2}-\d{2}(?:[ T]\d{2}:\d{2}(?::\d{2})?(?:\s*(?:AM|PM|am|pm))?)?|"
            r"\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4}(?:\s+\d{1,2}:\d{2}(?::\d{2})?(?:\s*(?:AM|PM|am|pm))?)?|"
            r"\d{1,2}[\s\-]+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s\-]+\d{4}(?:\s+\d{1,2}:\d{2}(?::\d{2})?(?:\s*(?:AM|PM|am|pm))?)?)\b",
            text_content,
            re.IGNORECASE,
        )

        # Identify Currency
        detected_currency = "BDT"
        if "SGD" in text_content.upper() or "SINGAPORE" in text_content.upper() or "PAYNOW" in text_content.upper():
            detected_currency = "SGD"
        elif "USD" in text_content.upper() or "USDT" in text_content.upper():
            detected_currency = "USD"

        # Detect Payment Method
        detected_method = None
        for method in ["bKash", "Nagad", "Rocket", "Upay", "PayNow", "FAST", "Bank Transfer", "Credit Card", "Crypto"]:
            if re.search(rf"\b{method}\b", text_content, re.IGNORECASE):
                detected_method = method
                break

        # Extract Recipient Account / Phone
        recipient_acc = None
        recipient_match = re.search(r"(?:To|Recipient|Receiver|Payee|Account|Wallet)[:\s]+(\+?[0-9]{8,16})", text_content, re.IGNORECASE)
        if recipient_match:
            recipient_acc = recipient_match.group(1)

        # Extract Sender Account / Phone
        sender_acc = None
        sender_match = re.search(r"(?:From|Sender|Payer)[:\s]+(\+?[0-9]{8,16})", text_content, re.IGNORECASE)
        if sender_match:
            sender_acc = sender_match.group(1)

        primary_amt = None
        if amt_matches:
            raw_amt_str = amt_matches[0].replace(",", "")
            try:
                primary_amt = float(raw_amt_str)
            except ValueError:
                primary_amt = None

        primary_tx_id = trx_matches[0] if trx_matches else None
        primary_ts = timestamp_matches[0] if timestamp_matches else None

        # Check for multi-transaction statements / receipts
        raw_lines = text_content.splitlines()
        tx_blocks = []
        current_block = []
        for line in raw_lines:
            if re.search(r"(?:Transaction\s+\d+|TrxID[:\s]|Txn ID[:\s]|Payment \d+:|Ref ID[:\s])", line, re.IGNORECASE):
                if current_block:
                    tx_blocks.append("\n".join(current_block))
                    current_block = []
            current_block.append(line)
        if current_block:
            tx_blocks.append("\n".join(current_block))

        if len(tx_blocks) > 1 and len(trx_matches) > 1:
            for b_idx, block in enumerate(tx_blocks, start=1):
                b_trx = re.findall(r"(?:TrxID|Txn ID|Transaction ID|Ref ID|Reference Number|UTR)[:\s]+([A-Za-z0-9]{8,24})", block, re.IGNORECASE)
                b_amt = re.findall(r"(?:BDT|TK|৳|SGD|\$|USD|Amount[:\s]+)\s?((?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{1,2})?)", block, re.IGNORECASE)
                b_ts = re.findall(r"\b(\d{4}-\d{2}-\d{2}(?:[ T]\d{2}:\d{2}(?::\d{2})?(?:\s*(?:AM|PM|am|pm))?)?|\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4}(?:\s+\d{1,2}:\d{2}(?::\d{2})?(?:\s*(?:AM|PM|am|pm))?)?)\b", block)
                b_rec = re.search(r"(?:To|Recipient|Receiver|Payee|Account|Wallet)[:\s]+(\+?[0-9]{8,16})", block, re.IGNORECASE)

                if b_trx or b_amt:
                    parsed_amt = 0.0
                    if b_amt:
                        try:
                            parsed_amt = float(b_amt[0].replace(",", ""))
                        except ValueError:
                            parsed_amt = 0.0
                    transactions.append(
                        ExtractedTransaction(
                            transaction_id=b_trx[0] if b_trx else f"TX-{sha256_hash[:6].upper()}-{b_idx}",
                            amount=parsed_amt,
                            currency=detected_currency,
                            timestamp=b_ts[0] if b_ts else primary_ts,
                            sender=sender_acc,
                            sender_account=sender_acc,
                            recipient=b_rec.group(1) if b_rec else recipient_acc,
                            recipient_account=b_rec.group(1) if b_rec else recipient_acc,
                            payment_method=detected_method or ("bKash" if detected_currency == "BDT" else "PayNow"),
                            reference_note=f"Transaction {b_idx} extracted from statement",
                            confidence=0.88,
                            source_file=filename,
                        )
                    )

        if not transactions and (primary_tx_id or primary_amt or ev_type == EvidenceType.TRANSACTION_RECEIPT):
            transactions.append(
                ExtractedTransaction(
                    transaction_id=primary_tx_id or f"TX-{sha256_hash[:8].upper()}",
                    amount=primary_amt or 0.0,
                    currency=detected_currency,
                    timestamp=primary_ts,
                    sender=sender_acc,
                    sender_account=sender_acc,
                    recipient=recipient_acc,
                    recipient_account=recipient_acc,
                    payment_method=detected_method or ("bKash" if detected_currency == "BDT" else "PayNow"),
                    reference_note="Extracted from evidence document",
                    confidence=0.88,
                    source_file=filename,
                )
            )

        summary = f"Ingested {ev_type.value} file '{filename}'."
        if transactions and transactions[0].amount:
            total_extracted = sum(t.amount or 0.0 for t in transactions)
            summary += f" Detected {len(transactions)} financial transaction(s): {detected_currency} {total_extracted:,.2f} via {transactions[0].payment_method or 'transfer'}."
        if entities:
            summary += f" Identified {len(entities)} relevant forensic entities."

        return EvidenceItem(
            item_id=item_id,
            filename=filename,
            file_type=detected_mime,
            sha256_hash=sha256_hash,
            evidence_type=ev_type,
            raw_text=text_content[:2000] if text_content else None,
            extracted_entities=entities,
            extracted_transactions=transactions,
            timestamps_found=timestamp_matches[:5],
            summary=summary,
            confidence=0.90,
            metadata={"source": "deterministic_fallback"},
        )
