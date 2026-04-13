"""
GMIF Classifier - Graphical Meta-Information Framework

Based on epistemic-memory-architecture's GMIF system.
Categorizes content by epistemic confidence level.
"""

import logging
from typing import Optional, List, Dict
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class GMIFType(str, Enum):
    """GMIF classification types."""
    M1_PRIMARY_EVIDENCE = "M1"  # High confidence, multiple sources
    M2_CONTEXTUAL_CONDITION = "M2"  # With assumptions
    M3_PARTIAL_DESCRIPTION = "M3"  # Unclassified
    M4_DOUBTFUL_TESTIMONY = "M4"  # Contradictions detected
    M5_INTERPRETATION = "M5"  # Clear basis, no contestation
    M6_DERIVED_EVIDENCE = "M6"  # Derived from alignment
    M7_SYNTHESIS = "M7"  # Final decision


@dataclass
class GMIFClassification:
    """Result of GMIF classification."""
    type: GMIFType
    confidence: float
    sources: List[str]
    assumptions: List[str]
    contradictions: List[str]
    risks: List[str]
    description: str


class GMIFClassifier:
    """
    Classifies content by epistemic confidence level.
    
    Categories:
    - M1: Primary Evidence - multiple legal sources, no contradictions
    - M2: Contextual Condition - with assumptions needing validation
    - M3: Partial Description - unclassified
    - M4: Doubtful Testimony - contradictory sources
    - M5: Interpretation - clear basis, no contestation
    - M6: Derived Evidence - derived from alignment
    - M7: Synthesis - final aggregated decision
    """
    
    # Thresholds
    CONFIDENCE_HIGH = 0.8
    CONFIDENCE_MEDIUM = 0.5
    SOURCES_MIN_FOR_M1 = 2
    SOURCES_MIN_FOR_M5 = 1
    
    def classify(
        self,
        claim: str,
        confidence: float,
        sources: List[Dict],
        risks: List[str],
        assumptions: List[str],
        contradictions: Optional[List[Dict]] = None,
        is_aggregated: bool = False,
    ) -> GMIFClassification:
        """
        Classify a claim by GMIF type.
        
        Args:
            claim: The claim text
            confidence: Confidence score (0.0-1.0)
            sources: List of sources {id, type, reference}
            risks: Identified risks
            assumptions: Assumptions made
            contradictions: List of detected contradictions
            is_aggregated: If this is a synthesis
            
        Returns:
            GMIFClassification with full details
        """
        contradictions = contradictions or []
        
        # M4: Contradictions detected
        if contradictions:
            logger.info(f"Claim classified as M4 - contradictions detected")
            return GMIFClassification(
                type=GMIFType.M4_DOUBTFUL_TESTIMONY,
                confidence=confidence,
                sources=[s.get("id", "") for s in sources],
                assumptions=assumptions,
                contradictions=[c.get("description", "") for c in contradictions],
                risks=risks,
                description="Contradictory sources detected",
            )
        
        # M7: Final/aggregated decision
        if is_aggregated:
            return GMIFClassification(
                type=GMIFType.M7_SYNTHESIS,
                confidence=confidence,
                sources=[s.get("id", "") for s in sources],
                assumptions=assumptions,
                contradictions=[],
                risks=risks,
                description="Final aggregated result",
            )
        
        # M1: High confidence, multiple sources, no risks
        if (confidence >= self.CONFIDENCE_HIGH and 
            len(sources) >= self.SOURCES_MIN_FOR_M1 and 
            not risks and
            not assumptions):
            return GMIFClassification(
                type=GMIFType.M1_PRIMARY_EVIDENCE,
                confidence=confidence,
                sources=[s.get("id", "") for s in sources],
                assumptions=assumptions,
                contradictions=[],
                risks=risks,
                description="Multiple sources, high confidence, no risks",
            )
        
        # M5: Clear source, no risks
        if (len(sources) >= self.SOURCES_MIN_FOR_M5 and 
            confidence >= self.CONFIDENCE_MEDIUM and
            not risks):
            return GMIFClassification(
                type=GMIFType.M5_INTERPRETATION,
                confidence=confidence,
                sources=[s.get("id", "") for s in sources],
                assumptions=assumptions,
                contradictions=[],
                risks=risks,
                description="Clear source, no contestation",
            )
        
        # M2: With assumptions
        if assumptions and confidence >= self.CONFIDENCE_MEDIUM:
            return GMIFClassification(
                type=GMIFType.M2_CONTEXTUAL_CONDITION,
                confidence=confidence,
                sources=[s.get("id", "") for s in sources],
                assumptions=assumptions,
                contradictions=[],
                risks=risks,
                description="With assumptions needing validation",
            )
        
        # M6: Derived
        if "alignment" in risks or "derived" in str(assumptions).lower():
            return GMIFClassification(
                type=GMIFType.M6_DERIVED_EVIDENCE,
                confidence=confidence,
                sources=[s.get("id", "") for s in sources],
                assumptions=assumptions,
                contradictions=[],
                risks=risks,
                description="Derived from alignment or inference",
            )
        
        # M3: Default
        return GMIFClassification(
            type=GMIFType.M3_PARTIAL_DESCRIPTION,
            confidence=confidence,
            sources=[s.get("id", "") for s in sources],
            assumptions=assumptions,
            contradictions=[],
            risks=risks,
            description="Classification pending or undetermined",
        )
    
    def get_color(self, gmif_type: GMIFType) -> str:
        """Get color for GMIF type."""
        color_map = {
            GMIFType.M1_PRIMARY_EVIDENCE: "#4CAF50",  # green
            GMIFType.M2_CONTEXTUAL_CONDITION: "#FFC107",  # yellow
            GMIFType.M3_PARTIAL_DESCRIPTION: "#FF9800",  # orange
            GMIFType.M4_DOUBTFUL_TESTIMONY: "#F44336",  # red
            GMIFType.M5_INTERPRETATION: "#8BC34A",  # light green
            GMIFType.M6_DERIVED_EVIDENCE: "#03A9F4",  # light blue
            GMIFType.M7_SYNTHESIS: "#9C27B0",  # purple
        }
        return color_map.get(gmif_type, "#9E9E9E")
    
    def get_description(self, gmif_type: GMIFType) -> str:
        """Get human-readable description."""
        desc_map = {
            GMIFType.M1_PRIMARY_EVIDENCE: "Multiple sources, high confidence, no risks",
            GMIFType.M2_CONTEXTUAL_CONDITION: "With assumptions that need validation",
            GMIFType.M3_PARTIAL_DESCRIPTION: "Classification pending or undetermined",
            GMIFType.M4_DOUBTFUL_TESTIMONY: "Contradictory sources detected",
            GMIFType.M5_INTERPRETATION: "Clear source, no contestation",
            GMIFType.M6_DERIVED_EVIDENCE: "Derived from alignment or inference",
            GMIFType.M7_SYNTHESIS: "Final aggregated result",
        }
        return desc_map.get(gmif_type, "Unknown")
    
    def is_high_risk(self, gmif_type: GMIFType) -> bool:
        """Check if GMIF type indicates high risk."""
        return gmif_type in (GMIFType.M4_DOUBTFUL_TESTIMONY, GMIFType.M3_PARTIAL_DESCRIPTION)
    
    def requires_followup(self, gmif_type: GMIFType) -> bool:
        """Check if GMIF type requires follow-up."""
        return gmif_type in (
            GMIFType.M2_CONTEXTUAL_CONDITION,
            GMIFType.M3_PARTIAL_DESCRIPTION,
            GMIFType.M4_DOUBTFUL_TESTIMONY,
        )


# Singleton instance
_classifier: Optional[GMIFClassifier] = None


def get_gmif_classifier() -> GMIFClassifier:
    global _classifier
    if _classifier is None:
        _classifier = GMIFClassifier()
    return _classifier