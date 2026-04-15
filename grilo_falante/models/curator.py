"""Curator model — Human or LLM curator with accountability scoring"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator

from grilo_falante.models.enums import CuratorType


class Curator(BaseModel):
    """
    Curator model with accountability scoring.

    Curators can be human or LLM, and are accountable
    for their validation decisions.
    """

    id: Optional[int] = Field(default=None, description="Database ID")
    curator_key: str = Field(..., description="Unique curator identifier")
    name: str = Field(..., description="Display name")

    # Type
    curator_type: CuratorType = Field(default=CuratorType.HUMAN)

    # For LLM curators
    model_name: Optional[str] = Field(default=None, description="Model name for LLM curators")

    # Specializations
    specializations: list[str] = Field(default_factory=list, description="Topic specializations")

    # Accountability score (0.0 - 1.0)
    # 0.9-1.0: Trusted Curator (can validate Tier 1)
    # 0.7-0.9: Standard Curator
    # 0.5-0.7: Provisional Curator
    # 0.3-0.5: Probationary (needs peer review)
    # 0.0-0.3: SUSPENDED
    accountability_score: float = Field(default=0.5, ge=0.0, le=1.0)

    # Status
    is_active: bool = Field(default=True)
    last_activity: Optional[datetime] = Field(default=None)

    # Timestamps
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    class Config:
        use_enum_values = True

    @field_validator("accountability_score")
    @classmethod
    def validate_score(cls, v: float) -> float:
        """Validate score is in range."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Score must be between 0.0 and 1.0")
        return v

    @property
    def is_suspended(self) -> bool:
        """Check if curator is suspended."""
        return self.accountability_score < 0.3

    @property
    def can_validate_tier1(self) -> bool:
        """Check if curator can validate Tier 1 sources."""
        return self.accountability_score >= 0.9

    @property
    def can_override(self) -> bool:
        """Check if curator can override other curators."""
        return self.accountability_score >= 0.5

    @property
    def needs_peer_review(self) -> bool:
        """Check if curator needs peer review."""
        return self.accountability_score < 0.5

    def penalize(self, amount: float = 0.1) -> None:
        """Penalize curator for incongruence."""
        self.accountability_score = max(0.0, self.accountability_score - amount)

    def reward(self, amount: float = 0.05) -> None:
        """Reward curator for valid corrections."""
        self.accountability_score = min(1.0, self.accountability_score + amount)

    def decay(self, days: int = 180) -> None:
        """
        Apply decay for inactivity.

        If curator hasn't been active for `days`, apply decay.
        Max decay is 0.3 (to 0.0 minimum).
        """
        if self.last_activity:
            import datetime as dt
            if (datetime.utcnow() - self.last_activity).days >= days:
                self.accountability_score = max(0.0, self.accountability_score - 0.3)
