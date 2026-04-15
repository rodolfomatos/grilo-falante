"""Models package — Pydantic models for Grilo Falante"""

from grilo_falante.models.enums import (
    LegitimacyState,
    ValidationState,
    GMIFLevel,
    CycleState,
    ClaimType,
    GapStatus,
    GapType,
    CuratorType,
    SourceTier,
    EpistemicRole,
    Attribution,
    EvaluationDecision,
    EvaluationType,
)

from grilo_falante.models.claim import Claim, GovernedClaim
from grilo_falante.models.gap import Gap
from grilo_falante.models.curator import Curator
from grilo_falante.models.source import GovernedSource, ShadowDocument
from grilo_falante.models.session import SessionPreferences
from grilo_falante.models.study_plan import StudyPlan, StudyPlanStep
from grilo_falante.models.governance import GovernanceRecord

__all__ = [
    # Enums
    "LegitimacyState",
    "ValidationState",
    "GMIFLevel",
    "CycleState",
    "ClaimType",
    "GapStatus",
    "GapType",
    "CuratorType",
    "SourceTier",
    "EpistemicRole",
    "Attribution",
    "EvaluationDecision",
    "EvaluationType",
    # Models
    "Claim",
    "GovernedClaim",
    "Gap",
    "Curator",
    "GovernedSource",
    "ShadowDocument",
    "SessionPreferences",
    "StudyPlan",
    "StudyPlanStep",
    "GovernanceRecord",
]
