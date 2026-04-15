"""
grilo_falante — Epistemic Governance Regime for LLM Interactions

A cognitive governance system that prevents decisions from being made
without explicit method and visible human cost.
"""

__version__ = "3.0.0"
__author__ = "Rodolfo"

from grilo_falante.models.enums import (
    LegitimacyState,
    ValidationState,
    GMIFLevel,
    CycleState,
    ClaimType,
    GapStatus,
    CuratorType,
    SourceTier,
    EpistemicRole,
)
from grilo_falante.models.claim import Claim, GovernedClaim
from grilo_falante.models.gap import Gap
from grilo_falante.models.curator import Curator
from grilo_falante.models.source import GovernedSource, ShadowDocument
from grilo_falante.models.session import SessionPreferences
from grilo_falante.models.study_plan import StudyPlan, StudyPlanStep
from grilo_falante.models.governance import GovernanceRecord

__all__ = [
    # Version
    "__version__",
    # Enums
    "LegitimacyState",
    "ValidationState",
    "GMIFLevel",
    "CycleState",
    "ClaimType",
    "GapStatus",
    "CuratorType",
    "SourceTier",
    "EpistemicRole",
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
