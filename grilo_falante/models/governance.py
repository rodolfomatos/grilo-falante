"""Governance record model — Audit trail for decisions"""

from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field

from grilo_falante.models.enums import LegitimacyState, ValidationState


class GovernanceRecord(BaseModel):
    """
    Governance record model.

    Immutable audit trail of all governance decisions.
    """

    id: Optional[int] = Field(default=None, description="Database ID")
    record_key: str = Field(..., description="Unique record identifier")

    # What was decided
    entity_type: str = Field(..., description="Type: claim, gap, source, etc.")
    entity_id: int = Field(..., description="ID of the entity")
    entity_key: str = Field(..., description="Key of the entity")

    # Decision
    action: str = Field(..., description="Action taken: validate, reject, etc.")
    decision: str = Field(..., description="Decision made")
    reason: Optional[str] = Field(default=None, description="Reason for decision")

    # Previous state (for audit)
    previous_state: Optional[str] = Field(default=None)
    new_state: str = Field(..., description="New state after decision")

    # Who made the decision
    curator_id: Optional[int] = Field(default=None, description="Curator who decided")
    curator_key: Optional[str] = Field(default=None, description="Curator key")

    # Confidence
    curator_confidence: Optional[float] = Field(default=None, description="Curator's confidence in this decision")

    # Metadata
    metadata: dict = Field(default_factory=dict, description="Additional metadata")

    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True

    def to_ledger_entry(self) -> dict[str, Any]:
        """Convert to ledger entry format."""
        return {
            "record_key": self.record_key,
            "entity_type": self.entity_type,
            "entity_key": self.entity_key,
            "action": self.action,
            "decision": self.decision,
            "curator_key": self.curator_key,
            "timestamp": self.created_at.isoformat(),
            "reason": self.reason,
        }
