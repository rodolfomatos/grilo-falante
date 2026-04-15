"""
Enums — Core enumerations for Grilo Falante regime
"""

from enum import Enum


class LegitimacyState(str, Enum):
    """State of legitimacy for a claim or artifact."""

    UNVALIDATED = "unvalidated"  # Initial state
    CANDIDATA = "candidata"  # Materialized but not validated
    ASSERTED = "asserted"  # Validated and asserted
    SUSPENDED = "suspended"  # Validation challenged
    REJECTED = "rejected"  # Rejected
    UNDER_REVIEW = "under_review"  # In review process


class ValidationState(str, Enum):
    """State of validation process."""

    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    CORRECTED = "corrected"


class GMIFLevel(str, Enum):
    """
    Grilo Falante Information Quality Scale.

    M1: Primary empirical data - multiple independent sources
    M2: Contextual - valid under specific assumptions
    M3: Partial - structure support limited
    M4: Doubtful - contradictions detected
    M5: Interpretation - single clear source
    M6: Derived - logical inference from data
    M7: Synthesis - aggregated from multiple sources
    M8: Conclusion - provisional conclusion
    """

    M1_PRIMARY = "M1"  # Green - Primary empirical data
    M2_CONTEXTUAL = "M2"  # Yellow - Contextual condition
    M3_PARTIAL = "M3"  # Orange - Partial description
    M4_DOUBTFUL = "M4"  # Red - Doubtful testimony
    M5_INTERPRETATION = "M5"  # Yellow - Interpretation
    M6_DERIVED = "M6"  # Orange - Derived evidence
    M7_SYNTHESIS = "M7"  # Yellow - Synthesis
    M8_CONCLUSION = "M8"  # White - Conclusion

    @property
    def color(self) -> str:
        """Return the color associated with this level."""
        colors = {
            "M1": "#22c55e",  # Green
            "M2": "#eab308",  # Yellow
            "M3": "#f97316",  # Orange
            "M4": "#ef4444",  # Red
            "M5": "#eab308",  # Yellow
            "M6": "#f97316",  # Orange
            "M7": "#eab308",  # Yellow
            "M8": "#ffffff",  # White
        }
        return colors.get(self.value, "#9ca3af")

    @property
    def confidence_range(self) -> tuple[float, float]:
        """Return the expected confidence range for this level."""
        ranges = {
            "M1": (0.8, 1.0),
            "M2": (0.6, 0.9),
            "M3": (0.4, 0.7),
            "M4": (0.1, 0.5),
            "M5": (0.5, 0.8),
            "M6": (0.4, 0.7),
            "M7": (0.5, 0.8),
            "M8": (0.3, 0.7),
        }
        return ranges.get(self.value, (0.0, 1.0))

    @classmethod
    def from_score(cls, confidence: float) -> "GMIFLevel":
        """Infer GMIF level from confidence score."""
        if confidence >= 0.8:
            return cls.M1_PRIMARY
        elif confidence >= 0.6:
            return cls.M2_CONTEXTUAL
        elif confidence >= 0.4:
            return cls.M3_PARTIAL
        elif confidence >= 0.2:
            return cls.M5_INTERPRETATION
        else:
            return cls.M4_DOUBTFUL


class CycleState(str, Enum):
    """State of the cognitive cycle."""

    INACTIVE = "inactive"  # No active cycle
    LOADED = "loaded"  # Regime loaded
    ACTIVE = "active"  # Cycle active
    GOVERNING = "governing"  # Making governance decisions
    HIBERNATED = "hibernated"  # Temporarily suspended
    ERROR = "error"  # Error state


class ClaimType(str, Enum):
    """Type of epistemic claim."""

    CORE_CLAIM = "core_claim"  # Primary claim
    SUBSIDIARY_CLAIM = "subsidiary_claim"  # Supporting claim
    LIMITATION = "limitation"  # Claim about limitations
    METHODOLOGICAL = "methodological"  # About methodology
    INTERPRETIVE_CLAIM = "interpretive_claim"  # Interpretation
    PROJECTION = "projection"  # Projected claim (F2)
    REFUTATION = "refutation"  # Counter-claim


class GapStatus(str, Enum):
    """Status of a knowledge gap."""

    IDENTIFIED = "identified"  # Gap identified
    IN_PROGRESS = "in_progress"  # Being resolved
    RESOLVED = "resolved"  # Resolved
    ABANDONED = "abandoned"  # Resolution abandoned


class GapType(str, Enum):
    """
    Type of knowledge gap.

    TIPO A: Research Failure - no claims with sufficient score
    TIPO B: Confidence Mismatch - info without trackable provenance
    TIPO C: Explicit Uncertainty - cannot explain at child's level
    """

    TIPO_A_FAILURE = "tipo_a_failure"  # Research failure
    TIPO_B_MISMATCH = "tipo_b_mismatch"  # Confidence mismatch
    TIPO_C_EXPLICIT = "tipo_c_explicit"  # Explicit uncertainty


class CuratorType(str, Enum):
    """Type of curator."""

    HUMAN = "human"
    LLM = "llm"


class SourceTier(str, Enum):
    """Tier of trusted source."""

    TIER_1 = "tier_1"  # Automatically accepted
    TIER_2 = "tier_2"  # Requires human curation
    TIER_3 = "tier_3"  # Rejected


class EpistemicRole(str, Enum):
    """Epistemic role of a claim."""

    DESCRIPTIVE = "descriptive"  # Describes what is
    PRESCRIPTIVE = "prescriptive"  # Describes what should be
    LIMITATION = "limitation"  # Describes limits
    METHODOLOGICAL = "methodological"  # About method


class Attribution(str, Enum):
    """Attribution type for claims."""

    SOURCE_EXPLICIT = "source_explicit"  # Explicit in source
    SOURCE_IMPLICIT = "source_implicit"  # Implicit in source
    EDITORIAL_INFERENCE = "editorial_inference"  # Editorial inference
    DERIVED = "derived"  # Derived from other claims


class EvaluationDecision(str, Enum):
    """Decision on an evaluation."""

    APPROVED = "approved"
    REJECTED = "rejected"
    CORRECTED = "corrected"
    CONDITIONAL = "conditional"


class EvaluationType(str, Enum):
    """Type of evaluation."""

    VALIDATION = "validation"
    CORRECTION = "correction"
    APPEAL = "appeal"
