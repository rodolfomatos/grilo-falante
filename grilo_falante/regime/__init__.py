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

from .state import (
    CycleState,
    CycleContext,
    StateMachine,
    LegitimacyState,
    ValidationState,
    GMIFLevel,
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
from .acordar import (
    Acordar,
    AcordarResult,
)
from .pina import (
    PINAProtocol,
    PINADecision,
    NormativeCandidateRecord,
    PINAResult,
)
from .validate import (
    TransitionValidator,
    TransitionResult,
    EpistemicGraph,
)
from .stamp import (
    stamp_capsule,
    stamp_all_capsules,
    generate_capsule_header,
    extract_gmif_from_filename,
    CAPSULE_GMIF_DEFAULTS,
    GMIF_DESCRIPTIONS,
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
