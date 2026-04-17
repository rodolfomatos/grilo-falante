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

    Human-readable labels replacing cryptic M1-M8 codes:

    VERIFIED: Primary empirical data confirmed by multiple independent credible sources
    UNVERIFIED: Claim made but not yet verified against sources
    PARTIAL: Partially supported by available evidence
    CONFLICTED: Contradicting sources detected - claim disputed
    INTERPRETATION: Based on single source or expert interpretation
    DERIVED: Logical inference from available data
    SYNTHESIS: Aggregated from multiple sources with analysis
    CONCLUSION: Provisional conclusion pending further verification
    """

    # New human-readable labels
    VERIFIED = "VERIFIED"  # 🟢 Green - Primary empirical data confirmed
    UNVERIFIED = "UNVERIFIED"  # 🟡 Yellow - Claim not yet verified
    PARTIAL = "PARTIAL"  # 🟠 Orange - Partial evidence support
    CONFLICTED = "CONFLICTED"  # 🔴 Red - Contradicting sources
    INTERPRETATION = "INTERPRETATION"  # 🔵 Blue - Single source interpretation
    DERIVED = "DERIVED"  # 🟣 Purple - Logical inference from data
    SYNTHESIS = "SYNTHESIS"  # 🟤 Brown - Multiple source aggregation
    CONCLUSION = "CONCLUSION"  # ⚪ White - Provisional conclusion

    # Backward compatibility aliases (deprecated, use VERIFIED etc)
    M1_PRIMARY = "VERIFIED"
    M2_CONTEXTUAL = "UNVERIFIED"
    M3_PARTIAL = "PARTIAL"
    M4_DOUBTFUL = "CONFLICTED"
    M5_INTERPRETATION = "INTERPRETATION"
    M6_DERIVED = "DERIVED"
    M7_SYNTHESIS = "SYNTHESIS"
    M8_CONCLUSION = "CONCLUSION"

    @property
    def color(self) -> str:
        """Return the color associated with this level."""
        colors = {
            "VERIFIED": "#22c55e",  # Green
            "UNVERIFIED": "#eab308",  # Yellow
            "PARTIAL": "#f97316",  # Orange
            "CONFLICTED": "#ef4444",  # Red
            "INTERPRETATION": "#3b82f6",  # Blue
            "DERIVED": "#a855f7",  # Purple
            "SYNTHESIS": "#78716c",  # Brown
            "CONCLUSION": "#ffffff",  # White
            # Backward compatibility
            "M1": "#22c55e",
            "M2": "#eab308",
            "M3": "#f97316",
            "M4": "#ef4444",
            "M5": "#3b82f6",
            "M6": "#a855f7",
            "M7": "#78716c",
            "M8": "#ffffff",
        }
        return colors.get(self.value, "#9ca3af")

    @property
    def label(self) -> str:
        """Return human-readable label."""
        return self.value

    @property
    def confidence_range(self) -> tuple[float, float]:
        """Return the expected confidence range for this level."""
        ranges = {
            "VERIFIED": (0.8, 1.0),
            "UNVERIFIED": (0.3, 0.6),
            "PARTIAL": (0.4, 0.7),
            "CONFLICTED": (0.0, 0.4),
            "INTERPRETATION": (0.5, 0.8),
            "DERIVED": (0.4, 0.7),
            "SYNTHESIS": (0.5, 0.8),
            "CONCLUSION": (0.3, 0.7),
            # Backward compatibility
            "M1": (0.8, 1.0),
            "M2": (0.3, 0.6),
            "M3": (0.4, 0.7),
            "M4": (0.0, 0.4),
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
            return cls.VERIFIED
        elif confidence >= 0.6:
            return cls.UNVERIFIED
        elif confidence >= 0.4:
            return cls.PARTIAL
        elif confidence >= 0.2:
            return cls.INTERPRETATION
        else:
            return cls.CONFLICTED


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
