"""Study plan model — Learning path steps"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from grilo_falante.models.enums import GapStatus


class StudyPlanStep(BaseModel):
    """Single step in a study plan."""

    order: int = Field(..., description="Step order")
    description: str = Field(..., description="Step description")
    resources: list[str] = Field(default_factory=list, description="Resource keys")
    estimated_time: str = Field(default="15 min", description="Estimated time")
    status: str = Field(default="pending", description="pending, in_progress, completed")

    # For GAP steps
    gap_key: Optional[str] = Field(default=None, description="Related gap if any")


class StudyPlan(BaseModel):
    """
    Study plan model.

    Represents a learning path with steps for
    resolving gaps and learning topics.
    """

    id: Optional[int] = Field(default=None, description="Database ID")
    plan_key: str = Field(..., description="Unique plan identifier")
    gap_key: Optional[str] = Field(default=None, description="Related gap")

    # Topic
    topic: str = Field(..., description="Topic this plan addresses")

    # Steps
    steps: list[StudyPlanStep] = Field(default_factory=list)

    # Status
    status: GapStatus = Field(default=GapStatus.IDENTIFIED)

    # Progress
    current_step: int = Field(default=0, description="Current step index")
    completed_steps: int = Field(default=0, description="Number of completed steps")

    # Timestamps
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    class Config:
        use_enum_values = True

    @property
    def total_steps(self) -> int:
        """Total number of steps."""
        return len(self.steps)

    @property
    def progress_percentage(self) -> float:
        """Progress as percentage."""
        if self.total_steps == 0:
            return 0.0
        return (self.completed_steps / self.total_steps) * 100

    def next_step(self) -> Optional[StudyPlanStep]:
        """Get next pending step."""
        for step in self.steps:
            if step.status == "pending":
                return step
        return None
