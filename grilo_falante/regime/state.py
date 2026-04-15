"""
Grilo Falante Regime — Core State Machine and Lifecycle

State transitions:
    INACTIVE → LOADED → ACTIVE → GOVERNING ↔ HIBERNATED
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import uuid4


class LegitimacyState(Enum):
    SUSPENDED = "LEGITIMACY_SUSPENDED"
    ASSERTED = "LEGITIMACY_ASSERTED"


class ValidationState(Enum):
    ACCEPT = "ACCEPT"
    CONDITIONAL = "CONDITIONAL"
    REJECT = "REJECT"
    REEXECUTE = "REEXECUTE"


class GMIFLevel(Enum):
    M1_PRIMARY = "M1"
    M2_CONTEXTUAL = "M2"
    M3_PARTIAL = "M3"
    M4_DOUBTFUL = "M4"
    M5_INTERPRETATION = "M5"
    M6_DERIVED = "M6"
    M7_SYNTHESIS = "M7"
    M8_CONCLUSION = "M8"


class CycleState(Enum):
    INACTIVE = "INACTIVE"
    LOADED = "LOADED"
    ACTIVE = "ACTIVE"
    GOVERNING = "GOVERNING"
    HIBERNATED = "HIBERNATED"


@dataclass
class CycleContext:
    cycle_id: str
    state: CycleState = CycleState.INACTIVE
    started_at: datetime = field(default_factory=datetime.now)
    last_transition: Optional[datetime] = None
    current_graph: Optional[str] = None
    current_node: Optional[str] = None
    claims_count: int = 0
    nca_pending: int = 0
    ledger_entry_ids: list[str] = field(default_factory=list)
    is_exploratory: bool = True
    legitimacy_declared: bool = False
    temporal_anchor: Optional[str] = None
    intention: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "cycle_id": self.cycle_id,
            "state": self.state.value,
            "started_at": self.started_at.isoformat(),
            "last_transition": self.last_transition.isoformat() if self.last_transition else None,
            "current_graph": self.current_graph,
            "current_node": self.current_node,
            "claims_count": self.claims_count,
            "nca_pending": self.nca_pending,
            "is_exploratory": self.is_exploratory,
            "legitimacy_declared": self.legitimacy_declared,
            "temporal_anchor": self.temporal_anchor,
            "intention": self.intention,
        }


class StateMachine:
    """
    State machine managing regime cycle transitions.

    States:
        INACTIVE → LOADED → ACTIVE → GOVERNING ↔ HIBERNATED
    """

    def __init__(self):
        self.current_cycle: Optional[CycleContext] = None

    def start_cycle(self) -> CycleContext:
        """Start a new governed cycle"""
        self.current_cycle = CycleContext(
            cycle_id=self._generate_cycle_id()
        )
        self.transition_to(CycleState.LOADED)
        return self.current_cycle

    def transition_to(self, new_state: CycleState) -> bool:
        """Attempt to transition to a new state. Returns True if successful."""
        if self.current_cycle is None:
            return False

        current = self.current_cycle.state
        valid_transitions = self._get_valid_transitions(current)

        if new_state not in valid_transitions:
            return False

        self.current_cycle.state = new_state
        self.current_cycle.last_transition = datetime.now()
        return True

    def _get_valid_transitions(self, from_state: CycleState) -> list[CycleState]:
        """Get valid transitions from a given state"""
        transitions = {
            CycleState.INACTIVE: [CycleState.LOADED],
            CycleState.LOADED: [CycleState.ACTIVE, CycleState.INACTIVE],
            CycleState.ACTIVE: [CycleState.GOVERNING, CycleState.HIBERNATED, CycleState.LOADED],
            CycleState.GOVERNING: [CycleState.HIBERNATED, CycleState.ACTIVE],
            CycleState.HIBERNATED: [CycleState.GOVERNING, CycleState.ACTIVE],
        }
        return transitions.get(from_state, [])

    def load(self) -> bool:
        """Transition to LOADED state (LOAD command)"""
        if self.current_cycle is None:
            self.start_cycle()
        return self.transition_to(CycleState.LOADED)

    def activate(self) -> bool:
        """Transition to ACTIVE state (ACORDAR complete)"""
        if self.current_cycle is None:
            return False
        return self.transition_to(CycleState.ACTIVE)

    def govern(self) -> bool:
        """Transition to GOVERNING state"""
        if self.current_cycle is None:
            return False
        return self.transition_to(CycleState.GOVERNING)

    def hibernate(self) -> bool:
        """Transition to HIBERNATED state (VAI_DORMIR)"""
        if self.current_cycle is None:
            return False
        return self.transition_to(CycleState.HIBERNATED)

    def resume(self) -> bool:
        """Resume from hibernation to GOVERNING"""
        if self.current_cycle is None:
            return False
        if self.current_cycle.state == CycleState.HIBERNATED:
            return self.transition_to(CycleState.GOVERNING)
        return False

    def end_cycle(self):
        """End the current cycle"""
        if self.current_cycle:
            self.current_cycle.state = CycleState.INACTIVE

    def can_claim(self) -> bool:
        """Check if claims can be made in current state"""
        return self.current_cycle is not None and \
            self.current_cycle.state in [CycleState.ACTIVE, CycleState.GOVERNING]

    def can_promote(self) -> bool:
        """Check if content can be promoted (not exploratory, legitimacy declared)"""
        if not self.current_cycle:
            return False
        return not self.current_cycle.is_exploratory and \
            self.current_cycle.legitimacy_declared

    def set_exploratory(self, is_exploratory: bool):
        """Set whether current content is exploratory (non-promotable)"""
        if self.current_cycle:
            self.current_cycle.is_exploratory = is_exploratory

    def declare_legitimacy(self, declared: bool = True):
        """Declare legitimacy for promotion"""
        if self.current_cycle:
            self.current_cycle.legitimacy_declared = declared

    def set_position(self, graph_id: str, node_id: str):
        """Set current position in the epistemic graph"""
        if self.current_cycle:
            self.current_cycle.current_graph = graph_id
            self.current_cycle.current_node = node_id

    def set_temporal_anchor(self, anchor: str):
        """Set temporal anchor for ACORDAR"""
        if self.current_cycle:
            self.current_cycle.temporal_anchor = anchor

    def set_intention(self, intention: str):
        """Set intention for ACORDAR"""
        if self.current_cycle:
            self.current_cycle.intention = intention

    def increment_claims(self):
        """Increment claims counter"""
        if self.current_cycle:
            self.current_cycle.claims_count += 1

    def _generate_cycle_id(self) -> str:
        """Generate a unique cycle ID"""
        return f"CYCLE-{datetime.now().strftime('%y%m%d')}-{uuid4().hex[:8]}"

    def get_status(self) -> dict:
        """Get current status"""
        if self.current_cycle is None:
            return {"state": "NO_CYCLE", "active": False}

        return {
            **self.current_cycle.to_dict(),
            "active": self.current_cycle.state != CycleState.INACTIVE,
            "can_claim": self.can_claim(),
            "can_promote": self.can_promote(),
        }