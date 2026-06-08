"""Gap model — Knowledge gap tracking"""

from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field

from grilo_falante.models.enums import GapStatus, GapType


class Gap(BaseModel):
    """
    Knowledge gap model.

    Represents an identified gap in knowledge that needs
    to be resolved through school mode or other means.
    """

    id: Optional[int] = Field(default=None, description="Database ID")
    gap_key: str = Field(..., description="Unique gap identifier")
    gap_type: GapType = Field(default=GapType.TIPO_A_FAILURE)

    # Query that identified the gap
    query: str = Field(..., description="Original query that triggered gap")
    claim_template: dict = Field(default_factory=dict, description="Expected claim structure")

    # Why it's a gap
    reason: str = Field(..., description="Why this is a gap")
    expected_claim: Optional[str] = Field(default=None, description="What we expect to find")

    # Status
    status: GapStatus = Field(default=GapStatus.IDENTIFIED)

    # Resolution
    resolved_claim_id: Optional[int] = Field(
        default=None, description="Claim that resolved this gap"
    )
    resolved_by: Optional[int] = Field(default=None, description="Curator who resolved")
    resolved_at: Optional[datetime] = Field(default=None)

    # Related
    related_claim_ids: list[int] = Field(default_factory=list)

    # Timestamps
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    class Config:
        use_enum_values = True

    @property
    def is_resolved(self) -> bool:
        """Check if gap is resolved."""
        return self.status == GapStatus.RESOLVED

    @property
    def is_blocking(self) -> bool:
        """Check if gap should block operations."""
        return self.gap_type == GapType.TIPO_A_FAILURE and self.status == GapStatus.IDENTIFIED

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "id": self.id,
            "gap_key": self.gap_key,
            "gap_type": self.gap_type.value
            if isinstance(self.gap_type, GapType)
            else self.gap_type,
            "query": self.query,
            "reason": self.reason,
            "status": self.status.value if isinstance(self.status, GapStatus) else self.status,
            "is_resolved": self.is_resolved,
            "resolved_claim_id": self.resolved_claim_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if self.claim_template:
            result["claim_template"] = self.claim_template if isinstance(self.claim_template, dict) else {}
        return result

    def model_dump(self, **kwargs):
        """Pydantic v2 compatible method."""
        return self.to_dict()
