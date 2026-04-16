"""
ILHA Model - Context Memory System

Represents a moment-space-time aggregate of context.
Each ILHA contains:
- timestamp (NTP for objective time)
- participants
- topic
- pedras (reusable contexts)
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


class Pedra(BaseModel):
    """
    A reusable context that can travel between ILHAS.

    Think of it as a "story" from the interaction that can
    be retold in other contexts.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ilha_id: str
    author_id: str
    author_name: str
    content: str
    gmif_level: str = "M3"

    # Classification
    type: str = "claim"  # claim, question, reaction, gap
    is_gap: bool = False
    gap_question: Optional[str] = None

    # Reuse tracking
    reused_in: List[str] = Field(default_factory=list())

    # Metadata
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


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
