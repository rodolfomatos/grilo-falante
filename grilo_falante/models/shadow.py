"""
Shadow Document — Epistemological shadow document model

S(D) = {x | x é assumido, imposto ou produzido por D,
     mesmo que não seja afirmar em D}

Based on Grilo Falante canonical definitions from modelos_cognitivos.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class EpistemicUnit:
    """An epistemic unit extracted from a document."""

    id: str
    type: str  # factual, premise, inference, interpretation, rhetorical
    content: str
    page_ref: Optional[int] = None
    gmif_level: str = "M4"
    f1_or_f2: Optional[str] = None  # "f1" (explicit) or "f2" (implicit projection)


@dataclass
class ShadowDocument:
    """
    Shadow document model - epistemological analysis of a principal document.

    S(D) = {x | x é assumido, imposto ou produzido por D,
         mesmo que não seja afirmar em D}

    Two "travões" (brakes):
    - T1: Explicit normative effect (governs legitimate use)
    - T2: Limitation of consequences (excludes ethical/political judgments)
    """

    id: Optional[int] = None
    source_id: Optional[int] = None
    title: str = ""
    authors: List[str] = field(default_factory=list)
    source_type: str = "unknown"
    persistent_id: str = ""

    # Global epistemic classification
    evidence_level: str = "weak"  # complete, conditioned, weak, doubtful

    # Scope and limits
    scope: str = ""
    limits: List[str] = field(default_factory=list)

    # Decomposition into epistemic units
    epistemic_units: List[EpistemicUnit] = field(default_factory=list)

    # F1 (explicit claims) and F2 (implicit projections) counts
    f1_count: int = 0
    f2_count: int = 0

    # Assumptions and commitments
    assumptions: List[str] = field(default_factory=list)
    commitments: List[str] = field(default_factory=list)
    structural_limits: List[str] = field(default_factory=list)

    # Misuse risks
    misuse_risks: List[str] = field(default_factory=list)

    # T1: Normative effect (what it governs)
    normative_effect: str = ""

    # T2: Consequence limitations (what it excludes)
    consequence_limitations: List[str] = field(default_factory=list)

    # Synthesis
    epistemic_synthesis: str = ""  # demonstrates, suggests, does_not_support

    # Zones of uncertainty
    uncertainty_zones: List[str] = field(default_factory=list)

    # Final epistemic honesty note
    honesty_note: str = ""

    # Status
    status: str = "pending"  # pending, in_progress, completed, validated

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source_id": self.source_id,
            "title": self.title,
            "authors": self.authors,
            "source_type": self.source_type,
            "persistent_id": self.persistent_id,
            "evidence_level": self.evidence_level,
            "scope": self.scope,
            "limits": self.limits,
            "epistemic_units": [
                {
                    "id": u.id,
                    "type": u.type,
                    "content": u.content,
                    "page_ref": u.page_ref,
                    "gmif_level": u.gmif_level,
                    "f1_or_f2": u.f1_or_f2,
                }
                for u in self.epistemic_units
            ],
            "f1_count": self.f1_count,
            "f2_count": self.f2_count,
            "assumptions": self.assumptions,
            "commitments": self.commitments,
            "structural_limits": self.structural_limits,
            "misuse_risks": self.misuse_risks,
            "normative_effect": self.normative_effect,
            "consequence_limitations": self.consequence_limitations,
            "epistemic_synthesis": self.epistemic_synthesis,
            "uncertainty_zones": self.uncertainty_zones,
            "honesty_note": self.honesty_note,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


@dataclass
class ConceptualCapsule:
    """
    Conceptual Capsule - preserved validated concept.

    CC = <C, A, Σ, Δ>
    C: Content
    A: Scope
    Σ: Interpretation regime
    Δ: Normative effect
    """

    id: Optional[int] = None
    capsule_key: str = ""
    content: str = ""
    scope: str = ""  # A
    interpretation_regime: str = ""  # Σ
    normative_effect: str = ""  # Δ
    source_document_id: Optional[int] = None
    validation_status: str = "pending"
    created_by: str = "system"
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "capsule_key": self.capsule_key,
            "content": self.content,
            "scope": self.scope,
            "interpretation_regime": self.interpretation_regime,
            "normative_effect": self.normative_effect,
            "source_document_id": self.source_document_id,
            "validation_status": self.validation_status,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
