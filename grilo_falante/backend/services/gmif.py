"""
GMIF Classifier — Grilo Falante Information Quality Classification

Automatically classifies claims with GMIF levels (M1-M8).
"""

import json
from typing import Optional

from grilo_falante.models import GMIFLevel


class GMIFClassifier:
    """
    Service for classifying claims with GMIF levels.

    Uses heuristics and LLM-assisted classification when available.
    """

    # Keywords that indicate different levels
    LEVEL_KEYWORDS = {
        "M1": [
            "study shows",
            "research demonstrates",
            "data indicates",
            "experiment reveals",
            "measured",
            "observed",
            "recorded",
            "multiple sources confirm",
        ],
        "M2": [
            "under conditions",
            "assuming",
            "given that",
            "when applied to",
            "in the context of",
            "under the assumption",
        ],
        "M3": [
            "partially",
            "some evidence suggests",
            "limited data",
            "preliminary",
            "incomplete",
        ],
        "M4": [
            "contradicts",
            "disputes",
            "controversial",
            "unverified",
            "disputed",
            "conflicting",
        ],
        "M5": [
            "author argues",
            "according to",
            "interprets as",
            "suggests that",
            "this means",
        ],
        "M6": [
            "therefore",
            "implies",
            "consequently",
            "thus we conclude",
            "derived from",
            "infers that",
        ],
        "M7": [
            "synthesizing",
            "in summary",
            "overall",
            "combining these findings",
            "meta-analysis",
        ],
        "M8": [
            "provisional",
            "tentatively",
            "in conclusion",
            "suggests",
            "may be",
        ],
    }

    @classmethod
    def classify(cls, claim_text: str, source_count: int = 1) -> tuple[GMIFLevel, float]:
        """
        Classify a claim with GMIF level and confidence.

        Args:
            claim_text: The claim to classify
            source_count: Number of sources supporting the claim

        Returns:
            Tuple of (GMIFLevel, confidence_score)
        """
        claim_lower = claim_text.lower()

        # Count keyword matches
        level_scores = {}
        for level, keywords in cls.LEVEL_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw.lower() in claim_lower)
            if source_count >= 3:
                score *= 1.2  # Boost if multiple sources
            level_scores[level] = score

        # Find best matching level
        if max(level_scores.values()) > 0:
            best_level = max(level_scores, key=level_scores.get)
        else:
            # Default based on source count
            if source_count >= 3:
                best_level = "M1"
            elif source_count == 2:
                best_level = "M2"
            elif source_count == 1:
                best_level = "M5"
            else:
                best_level = "M4"

        # Calculate confidence
        confidence = cls._calculate_confidence(best_level, level_scores, source_count)

        # Map old codes to GMIFLevel enum values
        code_to_enum = {
            "M1": "VERIFIED",
            "M2": "UNVERIFIED",
            "M3": "PARTIAL",
            "M4": "CONFLICTED",
            "M5": "INTERPRETATION",
            "M6": "DERIVED",
            "M7": "SYNTHESIS",
            "M8": "CONCLUSION"
        }
        enum_value = code_to_enum[best_level]
        return GMIFLevel(enum_value), confidence

    @classmethod
    def _calculate_confidence(
        cls, level: str, scores: dict[str, float], source_count: int
    ) -> float:
        """Calculate confidence score for classification."""
        base_ranges = {
            "M1": (0.8, 1.0),
            "M2": (0.6, 0.9),
            "M3": (0.4, 0.7),
            "M4": (0.1, 0.5),
            "M5": (0.5, 0.8),
            "M6": (0.4, 0.7),
            "M7": (0.5, 0.8),
            "M8": (0.3, 0.7),
        }

        min_conf, max_conf = base_ranges.get(level, (0.3, 0.7))

        # Adjust based on keyword match strength
        match_strength = scores.get(level, 0) / max(sum(scores.values()), 1)

        # Adjust based on source count
        if level == "M1" and source_count < 2:
            min_conf *= 0.7
            max_conf *= 0.8

        confidence = min_conf + (max_conf - min_conf) * min(match_strength * 2, 1.0)
        return round(min(max(confidence, 0.0), 1.0), 2)

    @classmethod
    def get_description(cls, level: GMIFLevel) -> str:
        """Get human-readable description of GMIF level."""
        descriptions = {
            GMIFLevel.M1_PRIMARY: "Primary empirical data from multiple independent sources",
            GMIFLevel.M2_CONTEXTUAL: "Valid under specific conditions or assumptions",
            GMIFLevel.M3_PARTIAL: "Partial description with limited structure support",
            GMIFLevel.M4_DOUBTFUL: "Doubtful - contradictions or weak evidence detected",
            GMIFLevel.M5_INTERPRETATION: "Interpretation based on single clear source",
            GMIFLevel.M6_DERIVED: "Logically derived from other data",
            GMIFLevel.M7_SYNTHESIS: "Synthesis aggregated from multiple sources",
            GMIFLevel.M8_CONCLUSION: "Provisional conclusion pending further evidence",
        }
        return descriptions.get(level, "Unknown level")

    @classmethod
    def is_blocking(cls, level: GMIFLevel, confidence: float) -> bool:
        """Check if claim should block operations."""
        return level == GMIFLevel.M4_DOUBTFUL and confidence < 0.3
