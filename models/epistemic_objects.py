from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any


class PropositionRole(str, Enum):
    FOUNDATIONAL = "foundational"
    ASSUMPTION = "assumption"
    DERIVED = "derived"
    CONSTRAINT = "constraint"


class RelationType(str, Enum):
    SUPPORTS = "supports"
    DEPENDS_ON = "depends_on"
    CONTRADICTS = "contradicts"
    NARROWS = "narrows"
    EXTENDS = "extends"


class TensionType(str, Enum):
    CONTRADICTION = "contradiction"
    UNCERTAINTY = "uncertainty"
    INCOMPLETENESS = "incompleteness"
    COMPETING = "competing"


class TensionResolution(str, Enum):
    UNRESOLVED = "unresolved"
    RESOLVED = "resolved"
    SUSPENDED = "suspended"
    ACCEPTED = "accepted"


class PropositionLegitimacy(str, Enum):
    SUSPENDED = "LEGITIMACY_SUSPENDED"
    ASSERTED = "LEGITIMACY_ASSERTED"


class LoopStatus(str, Enum):
    OPEN = "OPEN"
    SCHEDULED = "SCHEDULED"
    SUSPENDED = "SUSPENDED"
    BLOCKED = "BLOCKED"
    CLOSED = "CLOSED"
    PROMOTED = "PROMOTED"


class LoopCriticality(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ClosureType(str, Enum):
    EVIDENCE_BASED = "evidence_based"
    TRUSTED_COMMITMENT = "trusted_commitment"
    SUSPENSION = "suspension"
    BLOCKED = "blocked"


class FalsificationStatus(str, Enum):
    PENDING = "pending"
    VALIDATED = "validated"
    FAILED = "failed"
    NOT_APPLICABLE = "not_applicable"


class ArtefactType(str, Enum):
    DOCUMENTO_SOMBRA = "DocumentoSombra"
    OBJETO_DIGITAL = "ObjetoDigital"
    CAPSULA_CONCEPTUAL = "CapsulaConceptual"


@dataclass
class FalsificationCondition:
    id: str
    proposition_id: str
    condition_text: str
    evidence_needed: str
    status: FalsificationStatus = FalsificationStatus.PENDING


@dataclass
class Proposition:
    id: str
    statement: str
    role: PropositionRole
    gmif_type: str
    legitimacy: PropositionLegitimacy = PropositionLegitimacy.SUSPENDED
    supporting_claim_ids: List[str] = field(default_factory=list)
    falsification_conditions: List[FalsificationCondition] = field(default_factory=list)
    boundary_conditions: str = ""
    confidence: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class PropositionDependency:
    from_proposition: str
    to_proposition: str
    relation_type: RelationType


@dataclass
class TensionRecord:
    id: str
    left_proposition_id: str
    right_proposition_id: str
    tension_type: TensionType
    severity: int
    resolution_status: TensionResolution = TensionResolution.UNRESOLVED


@dataclass
class OpenLoop:
    id: str
    source_type: str
    source_id: str
    status: LoopStatus = LoopStatus.OPEN
    criticality: LoopCriticality = LoopCriticality.MEDIUM
    closure_policy: str = ""
    trusted_commitment: Optional[Dict[str, Any]] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ClosureRecord:
    loop_id: str
    closure_type: ClosureType
    evidence: Optional[str] = None
    committed_by: Optional[str] = None
    closed_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class TrustedCommitment:
    id: str
    claim_id: str
    commitment_text: str
    materialization: str
    committed_by: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Artefact:
    type: ArtefactType
    id: str
    provenance: Dict[str, Any] = field(default_factory=dict)
    content: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())