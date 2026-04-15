"""Source model — Governed source and shadow document"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from grilo_falante.models.enums import SourceTier, ValidationState


class GovernedSource(BaseModel):
    """
    Governed source model.

    Represents a source document (paper, article, etc.)
    with full metadata and governance state.
    """

    id: Optional[int] = Field(default=None, description="Database ID")
    source_key: str = Field(..., description="Unique source identifier")

    # Basic metadata
    title: str = Field(..., description="Source title")
    authors: list[str] = Field(default_factory=list, description="Author list")
    year: Optional[int] = Field(default=None, description="Publication year")
    doi: Optional[str] = Field(default=None, description="DOI")
    url: Optional[str] = Field(default=None, description="URL")

    # Source classification
    source_type: str = Field(default="paper", description="Type of source")
    source_origin: str = Field(default="unknown", description="Origin (arxiv, openalex, etc.)")

    # Tier
    tier: SourceTier = Field(default=SourceTier.TIER_2)

    # Governance
    validation_status: ValidationState = Field(default=ValidationState.PENDING)

    # Ingestion
    ingestion_origin: str = Field(default="manual", description="How it was added")

    # Raw metadata (JSON)
    raw_metadata: dict = Field(default_factory=dict)

    # Timestamps
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    class Config:
        use_enum_values = True


class ShadowDocument(BaseModel):
    """
    Shadow document model.

    Represents the epistemic shadow of a source,
    including F1 (explicit claims) and F2 (projections).
    """

    id: Optional[int] = Field(default=None, description="Database ID")
    source_id: int = Field(..., description="Source this shadows")

    # Content
    factual_summary: str = Field(default="", description="Factual summary of source")
    projected_claims: list[str] = Field(default_factory=list, description="F2 projections")
    citations: list[dict] = Field(default_factory=list, description="Citations with pages")
    limits: list[str] = Field(default_factory=list, description="Limitations")
    misuse_risks: list[str] = Field(default_factory=list, description="Potential misuses")

    # Status
    status: ValidationState = Field(default=ValidationState.PENDING)

    # Validation notes
    validation_notes: Optional[str] = Field(default=None)

    # F1/F2 counts
    f1_count: int = Field(default=0, description="Number of F1 claims")
    f2_count: int = Field(default=0, description="Number of F2 projections")

    # Timestamps
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    class Config:
        use_enum_values = True

    def add_f1(self, claim_text: str) -> None:
        """Add F1 claim."""
        self.f1_count += 1

    def add_f2(self, projection_text: str) -> None:
        """Add F2 projection."""
        self.projected_claims.append(projection_text)
        self.f2_count += 1
