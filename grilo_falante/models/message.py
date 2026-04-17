"""Message model — Single message in a conversation"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Message(BaseModel):
    """
    Message model - a single message in a conversation.

    Can be from user or assistant, and tracks epistemic metadata.
    """

    id: Optional[int] = Field(default=None, description="Database ID")
    message_key: str = Field(..., description="Unique message identifier")
    conversation_id: int = Field(..., description="Parent conversation ID")

    # Content
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")

    # LLM Metadata
    model: Optional[str] = Field(default=None, description="Model used for response")
    tokens_used: Optional[int] = Field(default=None, description="Token count")
    inference_time_ms: Optional[int] = Field(default=None, description="Response time")

    # Epistemic state
    claims_detected: list[int] = Field(default_factory=list, description="Claim IDs detected")
    gaps_identified: list[int] = Field(default_factory=list, description="Gap IDs identified")
    gmif_level: Optional[str] = Field(default=None, description="GMIF classification level")

    # Timestamps
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "message_key": self.message_key,
            "conversation_id": self.conversation_id,
            "role": self.role,
            "content": self.content,
            "model": self.model,
            "tokens_used": self.tokens_used,
            "inference_time_ms": self.inference_time_ms,
            "claims_detected": self.claims_detected,
            "gaps_identified": self.gaps_identified,
            "gmif_level": self.gmif_level,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def to_summary(self) -> dict:
        """Convert to summary for conversation view."""
        return {
            "id": self.id,
            "message_key": self.message_key,
            "role": self.role,
            "content": self.content[:100] + "..." if len(self.content) > 100 else self.content,
            "claims_count": len(self.claims_detected),
            "gaps_count": len(self.gaps_identified),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }