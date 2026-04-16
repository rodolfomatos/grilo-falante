"""
ILHA Model - Context Memory System

Represents a moment-space-time aggregate of context.
Each ILHA contains:
- timestamp (NTP for objective time)
- participants
- topic
- pedras (reusable contexts)

PEDRA is an AGGREGATOR that can contain:
- ShadowDocuments (shadows of sources)
- ConceptualCapsules (validated synthesis - is a DigitalObject)
- DigitalObjects (PDFs, URLs, images)
- Or be EMPTY if nothing relevant
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class InteractionType(str, Enum):
    """Type of interaction that generated the ILHA."""
    AI_TO_AI = "ai_to_ai"
    AI_TO_HUMAN = "ai_to_human"
    HUMAN_TO_HUMAN = "human_to_human"
    HUMAN_TO_AI = "human_to_ai"
    UNKNOWN = "unknown"


class Participant(BaseModel):
    """A participant in the interaction."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    role: str = "participant"  # e.g., "grilo-gf", "chatgpt", "human"
    type: str = "ai"  # "ai" or "human"


class GmifEvent(BaseModel):
    """
    A GMIF event in the timeline.
    Records when a classification occurred, not changes.
    """
    gmif_level: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source: str = "system"  # who/what classified
    note: Optional[str] = None


class ShadowDocument(BaseModel):
    """
    A shadow document - the shadow of a source.
    Like what remains when you remember a book - the claims, not the book.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_name: str  # e.g., "MemPalace README"
    source_type: str = "document"  # document, url, book, article
    source_reference: Optional[str] = None  # URL or path

    # Feynman layers
    feynman_f1: Optional[str] = None  # For children
    feynman_f2: Optional[str] = None  # For experts
    feynman_f3_gaps: List[str] = Field(default_factory=list())  # Why loop gaps

    # Claims extracted
    extracted_claims: List[str] = Field(default_factory=list())

    # Epistemic metadata
    evidence_level: str = "weak"  # complete, conditioned, weak, doubtful
    assumptions: List[str] = Field(default_factory=list())
    misuse_risks: List[str] = Field(default_factory=list())

    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class DigitalObject(BaseModel):
    """
    A digital object - referenceable entity.
    PDFs, URLs, images, files.
    Has identity, purpose, boundaries, authority, lifecycle.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str = "reference"  # pdf, url, image, file
    reference: str  # URL or path
    title: Optional[str] = None
    description: Optional[str] = None

    # Digital object properties
    identity: Optional[str] = None  # What it is
    purpose: Optional[str] = None  # Why it exists
    authority: Optional[str] = None  # Who controls it

    # If this is a ConceptualCapsule (validated synthesis)
    is_capsule: bool = False
    capsule_scope: Optional[str] = None  # A in CC=<C,A,Σ,Δ>
    capsule_interpretation: Optional[str] = None  # Σ in CC=<C,A,Σ,Δ>
    capsule_normative_effect: Optional[str] = None  # Δ in CC=<C,A,Σ,Δ>

    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ConceptualCapsule(BaseModel):
    """
    A ConceptualCapsule is a DigitalObject with closed, validated synthesis.
    It's everything needed to replicate an idea in another context.

    CC = <C, A, Σ, Δ>
    C: Content
    A: Scope
    Σ: Interpretation regime
    Δ: Normative effect

    Note: This is now modeled as a DigitalObject with is_capsule=True.
    This class is kept for semantic clarity.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str  # C: Content
    scope: str = ""  # A: Scope
    interpretation_regime: str = ""  # Σ: Interpretation regime
    normative_effect: str = ""  # Δ: Normative effect

    # Links
    source_document_id: Optional[str] = None
    validation_status: str = "pending"  # pending, validated, rejected

    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    validated_at: Optional[str] = None


class PedraType(str, Enum):
    """Type of pedra content."""
    CLAIM = "claim"
    QUESTION = "question"
    REACTION = "reaction"
    GAP = "gap"
    CONCEPT = "concept"
    PROCESS = "process"
    REFERENCE = "reference"


class Pedra(BaseModel):
    """
    A reusable context that can travel between ILHAS.

    Think of it as a "story" from the interaction that can
    be retold in other contexts.

    PEDRA is an AGGREGATOR that can contain:
    - ShadowDocuments (shadows of sources)
    - DigitalObjects (PDFs, URLs, images)
    - ConceptualCapsules (DigitalObjects with is_capsule=True)
    - Or be EMPTY if nothing relevant

    A pedra is delimited by SIGNIFICANT EVENTS, not time.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ilha_id: str

    # Temporal dimension - delimited by events
    started_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    ended_at: Optional[str] = None  # None if still active

    # Author
    author_id: str
    author_name: str

    # Content summary (for display)
    content_summary: str = ""

    # AGGREGATOR: Can contain any combination
    shadow_documents: List[ShadowDocument] = Field(default_factory=list())
    digital_objects: List[DigitalObject] = Field(default_factory=list())
    # ConceptualCapsules are DigitalObjects with is_capsule=True

    # If empty, no relevant content
    is_empty: bool = True

    # GMIF tracking (timeline, not state)
    gmif_events: List[GmifEvent] = Field(default_factory=list())
    gmif_level: str = "M3"  # Current classification

    # Classification
    type: PedraType = PedraType.CLAIM
    is_gap: bool = False
    gap_question: Optional[str] = None

    # Saliência (relevance)
    saliencia: float = 0.5  # 0-1, can grow or decay
    consequence_level: float = 0.0  # 0-1
    decay_enabled: bool = True

    # Reuse tracking
    reused_in: List[str] = Field(default_factory=list())

    # Metadata
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    class Config:
        from_attributes = True


class ILHA(BaseModel):
    """
    ILHA - Moment-space-time aggregate of context.

    The ILHA is the fundamental unit of memory in Grilo Falante.
    It represents a specific moment in time with participants,
    a topic, and multiple perspectives (pedras).

    Think of it like a party - the party is a moment (ILHA),
    and each guest has their perspective (pedras).
    """
    id: str = Field(default_factory=lambda: f"ILHA-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    ntp_timestamp: Optional[float] = None  # Unix timestamp for external sync

    # Participants
    participants: List[Participant] = Field(default_factory=list())

    # Topic
    topic: str = ""
    topic_summary: Optional[str] = None

    # Type
    interaction_type: InteractionType = InteractionType.UNKNOWN

    # Content
    pedras: List[Pedra] = Field(default_factory=list())

    # Statistics
    claims_count: int = 0
    gaps_count: int = 0
    questions_count: int = 0

    # GMIF summary
    gmif_summary: Dict[str, int] = Field(default_factory=dict())

    # Reuse
    reused_pedras: List[str] = Field(default_factory=list())  # PEDRA IDs that traveled here

    # Status
    is_processed: bool = False
    processed_at: Optional[str] = None

    # Logbook metadata
    title: str = ""  # Human-readable title for logbook

    class Config:
        from_attributes = True


class ILHACreate(BaseModel):
    """Request to create a new ILHA."""
    topic: str
    participants: List[Dict[str, str]] = Field(default_factory=list())
    interaction_type: InteractionType = InteractionType.UNKNOWN
    title: Optional[str] = None


class ILHAUpdate(BaseModel):
    """Request to update an ILHA."""
    title: Optional[str] = None
    topic_summary: Optional[str] = None
    is_processed: Optional[bool] = None


class LogbookEntry(BaseModel):
    """An entry in the logbook, representing an ILHA."""
    id: str
    timestamp: str
    title: str
    topic: str
    interaction_type: str
    participants: List[str]  # Names only
    pedras_count: int
    claims_count: int
    gaps_count: int
    gmif_summary: Dict[str, int]
    is_processed: bool


class ConversationMessage(BaseModel):
    """A message in the conversation that generated an ILHA."""
    participant: str
    content: str
    claims_extracted: List[str] = Field(default_factory=list())
    gaps_extracted: List[str] = Field(default_factory=list())


class ILHAFromConversation(BaseModel):
    """ILHA generated from an AI-to-AI or similar conversation."""
    topic: str
    messages: List[ConversationMessage] = Field(default_factory=list())
    gmif_distribution: Dict[str, int] = Field(default_factory=dict())
    gaps_found: List[str] = Field(default_factory=list())
    pedras_created: int = 0
