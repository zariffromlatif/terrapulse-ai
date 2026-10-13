"""Central investigation service coordinating evidence ingestion, verification, intelligence, and dossier generation."""

from __future__ import annotations

import datetime
import uuid
from typing import Any, Dict, List, Optional, Tuple
from proofpath.dossier import DossierGenerator
from proofpath.extractor import EvidenceExtractor
from proofpath.graph import ScamIntelligenceGraph
from proofpath.models import (
    CaseDossier,
    EvidenceItem,
    EvidenceType,
    Jurisdiction,
)
from proofpath.response_agent import ProceduralResponseAgent
from proofpath.verification import VerificationEngine


class ProofPathService:
    """Orchestrates end-to-end evidence reconstruction, risk analysis, and response generation."""

    def __init__(self, api_key: Optional[str] = None):
        self.extractor = EvidenceExtractor(api_key=api_key)
        self.verification_engine = VerificationEngine()
        self.intelligence_graph = ScamIntelligenceGraph()
        self.response_agent = ProceduralResponseAgent()
        self.dossier_generator = DossierGenerator()
        self._cases: Dict[str, CaseDossier] = {}

    def analyze_case(
        self,
        files: List[Tuple[str, bytes, Optional[str]]],
        jurisdiction: Jurisdiction = Jurisdiction.BANGLADESH,
        victim_name: str = "Confidential Victim",
        victim_contact: str = "Confidential Contact",
        case_id: Optional[str] = None,
    ) -> CaseDossier:
        """Process multiple multimodal evidence files into an evidence-backed case dossier."""
        cid = case_id or f"PP-{datetime.datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

        # 1. Ingest and extract structured facts for each evidence file
        evidence_items: List[EvidenceItem] = []
        for filename, content_bytes, mime_type in files:
            item = self.extractor.process_file_content(
                filename=filename,
                content_bytes=content_bytes,
                mime_type=mime_type,
            )
            evidence_items.append(item)

        # 2. Verification & Risk Engine
        risk_assessment, chronology = self.verification_engine.verify_case(evidence_items)

        # 3. Cross-Case Scam Intelligence
        syndicate_matches = self.intelligence_graph.find_syndicate_matches(evidence_items)

        # Calculate Total Verified Loss & Currency
        # Receipts take absolute precedence over solicitations in chats
        receipt_items = [it for it in evidence_items if it.evidence_type == EvidenceType.TRANSACTION_RECEIPT]
        items_for_loss = receipt_items if receipt_items else evidence_items

        total_loss = 0.0
        seen_tx_ids = set()
        currency = "BDT" if jurisdiction == Jurisdiction.BANGLADESH else "SGD"

        for item in items_for_loss:
            for tx in item.extracted_transactions:
                tx_id = tx.transaction_id
                if tx_id and tx_id in seen_tx_ids:
                    continue
                if tx_id:
                    seen_tx_ids.add(tx_id)

                if tx.amount:
                    total_loss += tx.amount
                if tx.currency:
                    currency = tx.currency

        # Link into graph
        self.intelligence_graph.link_case_to_graph(
            case_id=cid,
            evidence_items=evidence_items,
            pattern_name=risk_assessment.primary_scam_pattern,
            total_loss=total_loss,
        )

        # 4. Procedural Response Agent
        roadmap = self.response_agent.generate_roadmap(
            jurisdiction=jurisdiction,
            evidence_items=evidence_items,
            risk_assessment=risk_assessment,
            total_loss=total_loss,
            currency=currency,
        )

        complaint_drafts = self.response_agent.generate_complaint_drafts(
            jurisdiction=jurisdiction,
            case_id=cid,
            victim_name=victim_name,
            victim_contact=victim_contact,
            evidence_items=evidence_items,
            risk_assessment=risk_assessment,
            total_loss=total_loss,
            currency=currency,
        )

        summary = (
            f"Case {cid} comprises {len(evidence_items)} forensic artifacts totaling {currency} {total_loss:,.2f} in verified losses. "
            f"Primary pattern classified as '{risk_assessment.primary_scam_pattern}' with {risk_assessment.risk_level} threat level "
            f"({risk_assessment.risk_score:.0f}/100). "
            f"{len(risk_assessment.contradictions)} forensic contradiction(s) and {len(syndicate_matches)} syndicate cluster match(es) identified."
        )

        dossier = CaseDossier(
            case_id=cid,
            created_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            victim_name=victim_name,
            victim_contact=victim_contact,
            jurisdiction=jurisdiction,
            summary=summary,
            evidence_items=evidence_items,
            chronology=chronology,
            risk_assessment=risk_assessment,
            syndicate_matches=syndicate_matches,
            procedural_roadmap=roadmap,
            complaint_drafts=complaint_drafts,
            total_loss_amount=total_loss,
            total_loss_currency=currency,
        )

        self._cases[cid] = dossier
        return dossier

    def get_case(self, case_id: str) -> Optional[CaseDossier]:
        return self._cases.get(case_id)

    def get_graph_data(self) -> Dict[str, Any]:
        return self.intelligence_graph.export_graph_json()

    def get_pdf(self, case_id: str) -> Optional[bytes]:
        dossier = self.get_case(case_id)
        if not dossier:
            return None
        return self.dossier_generator.generate_pdf(dossier)

    def get_zip(self, case_id: str) -> Optional[bytes]:
        dossier = self.get_case(case_id)
        if not dossier:
            return None
        return self.dossier_generator.generate_zip_packet(dossier)
