"""
Grilo Falante Regime — Epistemic Governance Lifecycle

State Machine:
    INACTIVE → LOADED → ACTIVE → GOVERNING ↔ HIBERNATED

Core Components:
- StateMachine: Manages cycle state transitions
- Loader: Activates/deactivates the regime
- Acordar: Wake-up ritual with temporal anchoring
- Ledger: Persistent audit trail
"""

from .acordar import (
    Acordar,
    AcordarResult,
    GitContext,
    IslandContext,
)
from .ledger import (
    Ledger,
    LedgerEntry,
    LedgerEntryType,
)
from .loader import (
    Loader,
    LoadResult,
    SystemUseRecord,
)
from .pina import (
    NormativeCandidateRecord,
    PINADecision,
    PINAProtocol,
    PINAResult,
)
from .stamp import (
    CAPSULE_GMIF_DEFAULTS,
    GMIF_DESCRIPTIONS,
    extract_gmif_from_filename,
    generate_capsule_header,
    stamp_all_capsules,
    stamp_capsule,
)
from .state import (
    CycleContext,
    CycleState,
    GMIFLevel,
    LegitimacyState,
    StateMachine,
    ValidationState,
)
from .validate import (
    EpistemicGraph,
    TransitionResult,
    TransitionValidator,
)

__version__ = "3.0.0"
__all__ = [
    "CycleState",
    "CycleContext",
    "StateMachine",
    "LegitimacyState",
    "ValidationState",
    "GMIFLevel",
    "Ledger",
    "LedgerEntry",
    "LedgerEntryType",
    "Loader",
    "LoadResult",
    "SystemUseRecord",
    "Acordar",
    "AcordarResult",
    "GitContext",
    "IslandContext",
    "PINAProtocol",
    "PINADecision",
    "NormativeCandidateRecord",
    "PINAResult",
    "TransitionValidator",
    "TransitionResult",
    "EpistemicGraph",
    "stamp_capsule",
    "stamp_all_capsules",
    "generate_capsule_header",
    "extract_gmif_from_filename",
    "CAPSULE_GMIF_DEFAULTS",
    "GMIF_DESCRIPTIONS",
]
