"""Session model — Session preferences for filtering"""

from typing import Optional
from pydantic import BaseModel, Field

from grilo_falante.models.enums import GMIFLevel


class SessionPreferences(BaseModel):
    """
    Session preferences model.

    Stores user preferences for a session including
    topics, domains, and epistemic filters.
    """

    session_id: str = Field(..., description="Unique session identifier")

    # Interests
    topics: list[str] = Field(default_factory=list, description="Topic interests")
    domains: list[str] = Field(default_factory=list, description="Domain interests")

    # Recency weighting (0.0 - 1.0)
    recency_weight: float = Field(default=0.3, ge=0.0, le=1.0)

    # Preferred GMIF categories
    preferred_categories: list[str] = Field(
        default=["M1", "M2", "M5", "M7"],
        description="Preferred GMIF levels"
    )

    # Display preferences
    show_metadata: bool = Field(default=True, description="Show provenance metadata")
    auto_school_mode: bool = Field(default=True, description="Auto-trigger school mode")
    confidence_display: str = Field(default="full", description="Display level: full, brief, none")

    class Config:
        use_enum_values = True

    def get_preferred_levels(self) -> list[GMIFLevel]:
        """Get preferred GMIF levels as enum."""
        levels = []
        for cat in self.preferred_categories:
            try:
                levels.append(GMIFLevel(cat))
            except ValueError:
                pass
        return levels

    def should_auto_school(self, gap_count: int) -> bool:
        """Determine if auto school mode should trigger."""
        return self.auto_school_mode and gap_count > 0
