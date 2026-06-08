"""Claim model — Core epistemic claim"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from grilo_falante.models.enums import (
    LegitimacyState,
    ValidationState,
    GMIFLevel,
    ClaimType,
    Attribution,
    EpistemicRole,
)


class Claim(BaseModel):
    """Base claim model."""

    claim_key: str = Field(..., description="Unique identifier for the claim")
    claim_text: str = Field(..., description="The actual claim content")
    claim_type: ClaimType = Field(default=ClaimType.CORE_CLAIM)

    class Config:
        use_enum_values = True


class GovernedClaim(Claim):
    """
    Governed claim with full epistemic metadata.

    This is the core model for all claims in the system,
    tracking provenance, validation, and governance state.
    """

    id: Optional[int] = Field(default=None, description="Database ID")

    # Source tracking
    source_id: Optional[int] = Field(default=None, description="Source document ID")
    session_id: str = Field(default="global", description="Session where claim was created")

    # Epistemic classification
    gmif_level: GMIFLevel = Field(default=GMIFLevel.M4_DOUBTFUL)
    gmif_confidence: float = Field(default=0.5, ge=0.0, le=1.0)

    # Attribution
    attribution: Attribution = Field(default=Attribution.SOURCE_EXPLICIT)
    epistemic_role: EpistemicRole = Field(default=EpistemicRole.DESCRIPTIVE)

    # Governance state
    legitimacy_state: LegitimacyState = Field(default=LegitimacyState.UNVALIDATED)
    validation_status: ValidationState = Field(default=ValidationState.PENDING)

    # Provenance
    provenance: dict = Field(default_factory=dict, description="Provenance chain")

    # Usage tracking
    usage_count: int = Field(default=0, description="Number of times used")
    last_used: Optional[datetime] = Field(default=None)

    # Timestamps
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # GF-ID for traceability
    gfid: Optional[str] = Field(default=None, description="Grilo Falante ID")

    class Config:
        use_enum_values = True

    def mark_used(self) -> None:
        """Mark this claim as used."""
        self.usage_count += 1
        self.last_used = datetime.utcnow()

    def is_validated(self) -> bool:
        """Check if claim is in validated state."""
        return self.validation_status == ValidationState.APPROVED

    def is_blocking(self) -> bool:
        """Check if claim should block (M4 with low confidence)."""
        return self.gmif_level == GMIFLevel.M4_DOUBTFUL and self.gmif_confidence < 0.3

    def to_card(self) -> dict:
        """Convert to ClaimCard format for UI."""
        return {
            "id": self.id,
            "claim_key": self.claim_key,
            "claim_text": self.claim_text,
            "gmif_level": self.gmif_level.value
            if isinstance(self.gmif_level, GMIFLevel)
            else self.gmif_level,
            "gmif_confidence": self.gmif_confidence,
            "validation_status": self.validation_status.value
            if isinstance(self.validation_status, ValidationState)
            else self.validation_status,
            "legitimacy_state": self.legitimacy_state.value
            if isinstance(self.legitimacy_state, LegitimacyState)
            else self.legitimacy_state,
            "source_id": self.source_id,
            "provenance": self.provenance,
        }
