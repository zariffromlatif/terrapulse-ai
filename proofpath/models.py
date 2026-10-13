"""Data models and schemas for ProofPath AI."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EvidenceType(str, Enum):
    TRANSACTION_RECEIPT = "TRANSACTION_RECEIPT"
    CHAT_MESSAGE = "CHAT_MESSAGE"
    VOICE_NOTE = "VOICE_NOTE"
    CALL_LOG = "CALL_LOG"
    EMAIL = "EMAIL"
    PHISHING_PAGE = "PHISHING_PAGE"
    CONTRACT_DOCUMENT = "CONTRACT_DOCUMENT"
    OTHER = "OTHER"


class Jurisdiction(str, Enum):
    BANGLADESH = "BANGLADESH"
    SINGAPORE = "SINGAPORE"
    GENERAL = "GENERAL"


class Currency(str, Enum):
    BDT = "BDT"
    SGD = "SGD"
    USD = "USD"
    EUR = "EUR"
    INR = "INR"
    MYR = "MYR"
    OTHER = "OTHER"


class ExtractedEntity(BaseModel):
    entity_type: str = Field(..., description="e.g. phone_number, wallet_account, bank_account, domain, person_name")
    value: str
    normalized_value: str
    role: str = Field(default="suspect", description="victim, suspect, intermediary, platform")
    confidence: float = Field(default=0.9, ge=0.0, le=1.0)
    source_file: Optional[str] = None


class ExtractedTransaction(BaseModel):
    transaction_id: Optional[str] = None
    amount: Optional[float] = None
    currency: str = "BDT"
    timestamp: Optional[str] = None
    sender: Optional[str] = None
    sender_account: Optional[str] = None
    recipient: Optional[str] = None
    recipient_account: Optional[str] = None
    payment_method: Optional[str] = None
    reference_note: Optional[str] = None
    confidence: float = Field(default=0.9, ge=0.0, le=1.0)
    source_file: Optional[str] = None


class EvidenceItem(BaseModel):
    item_id: str
    filename: str
    file_type: str
    sha256_hash: str
    evidence_type: EvidenceType
    raw_text: Optional[str] = None
    extracted_entities: List[ExtractedEntity] = Field(default_factory=list)
    extracted_transactions: List[ExtractedTransaction] = Field(default_factory=list)
    timestamps_found: List[str] = Field(default_factory=list)
    summary: str = ""
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChronologicalEvent(BaseModel):
    sequence_number: int
    timestamp: Optional[str] = None
    event_type: str = "INTERACTION"
    description: str
    evidence_sources: List[str] = Field(default_factory=list)
    actors: List[str] = Field(default_factory=list)
    amount: Optional[float] = None
    currency: Optional[str] = None


class Contradiction(BaseModel):
    rule_id: str
    severity: str = "HIGH"  # HIGH, MEDIUM, LOW
    title: str
    description: str
    evidence_item_a: str
    evidence_item_b: Optional[str] = None
    conflicting_fields: Dict[str, Any] = Field(default_factory=dict)


class RiskAssessment(BaseModel):
    risk_score: float = Field(default=0.0, ge=0.0, le=100.0)
    risk_level: str = "LOW"  # CRITICAL, HIGH, MEDIUM, LOW
    primary_scam_pattern: str = "Unknown"
    secondary_patterns: List[str] = Field(default_factory=list)
    tactics_detected: List[str] = Field(default_factory=list)
    contradictions: List[Contradiction] = Field(default_factory=list)
    red_flags: List[str] = Field(default_factory=list)


class SyndicateMatch(BaseModel):
    cluster_id: str
    known_alias: Optional[str] = None
    matched_identifiers: List[str] = Field(default_factory=list)
    total_linked_cases: int = 1
    syndicate_confidence: float = 0.8
    notes: str = ""


class ProceduralStep(BaseModel):
    step_number: int
    stage: str
    authority_name: str
    contact_channel: str
    timeline_window: str
    instructions: str
    required_evidence: List[str] = Field(default_factory=list)
    statutory_reference: str


class ComplaintDraft(BaseModel):
    target_authority: str
    jurisdiction: str
    subject: str
    body: str
    exhibits_referenced: List[str] = Field(default_factory=list)


class CaseDossier(BaseModel):
    case_id: str
    created_at: str
    victim_name: Optional[str] = "Confidential Victim"
    victim_contact: Optional[str] = "Confidential Contact"
    jurisdiction: Jurisdiction = Jurisdiction.BANGLADESH
    summary: str
    evidence_items: List[EvidenceItem] = Field(default_factory=list)
    chronology: List[ChronologicalEvent] = Field(default_factory=list)
    risk_assessment: RiskAssessment = Field(default_factory=RiskAssessment)
    syndicate_matches: List[SyndicateMatch] = Field(default_factory=list)
    procedural_roadmap: List[ProceduralStep] = Field(default_factory=list)
    complaint_drafts: List[ComplaintDraft] = Field(default_factory=list)
    total_loss_amount: float = 0.0
    total_loss_currency: str = "BDT"
