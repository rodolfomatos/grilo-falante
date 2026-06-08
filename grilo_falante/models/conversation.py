"""Conversation model — Chat thread/conversation"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Conversation(BaseModel):
    """
    Conversation model - a thread of messages between user and assistant.

    Represents a single conversation session that can be continued over time.
    """

    id: Optional[int] = Field(default=None, description="Database ID")
    conversation_key: str = Field(..., description="Unique conversation identifier")
    title: str = Field(default="New Conversation", description="Conversation title")
    user_id: str = Field(default="anonymous", description="User who owns this conversation")

    # LLM Configuration
    model_used: Optional[str] = Field(default=None, description="LLM model used")
    system_prompt: Optional[str] = Field(default=None, description="System prompt for context")

    # Stats
    message_count: int = Field(default=0, description="Number of messages")
    claims_count: int = Field(default=0, description="Claims created in this conversation")
    gaps_count: int = Field(default=0, description="Gaps identified in this conversation")

    # Status
    is_archived: bool = Field(default=False, description="Is conversation archived")

    # Timestamps
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    last_message_at: Optional[datetime] = Field(default=None)

    class Config:
        use_enum_values = True

    def update_last_message(self) -> None:
        """Update timestamps after new message."""
        self.last_message_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def increment_message_count(self) -> None:
        """Increment message counter."""
        self.message_count += 1
        self.updated_at = datetime.utcnow()

    def to_summary(self) -> dict:
        """Convert to summary dict for listing."""
        return {
            "id": self.id,
            "conversation_key": self.conversation_key,
            "title": self.title,
            "message_count": self.message_count,
            "claims_count": self.claims_count,
            "gaps_count": self.gaps_count,
            "model_used": self.model_used,
            "is_archived": self.is_archived,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_message_at": self.last_message_at.isoformat() if self.last_message_at else None,
        }