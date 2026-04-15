"""
Grilo Falante PINA — Protocol for Normative Incorporation

PINA governs the transition from textual norm detection to operative
epistemic constraint.

Key rules:
- Detection of normative occurrences does NOT trigger PINA
- Only Normative Candidates (NCA) trigger the PINA decision gate
- Human authorization is required for incorporation
- Silence does not constitute a valid decision
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

from .state import StateMachine
from .ledger import Ledger, LedgerEntryType


class PINADecision(Enum):
    INCORPORATE = "A"
    DO_NOT_INCORPORATE = "B"
    DEFER = "C"


@dataclass
class NormativeCandidateRecord:
    nca_id: str
    source_document: str
    faithful_statement: str
    location: str
    graph_scope: Optional[str] = None
    decision: Optional[PINADecision] = None
    created_at: datetime = field(default_factory=datetime.now)
    decided_at: Optional[datetime] = None
    cycle_id: Optional[str] = None


@dataclass
class PINAResult:
    success: bool
    nca_id: str
    message: str
    decision: Optional[str] = None
    active_invariants: int = 0


class PINAProtocol:
    """
    Protocol for Normative Incorporation (PINA).
    """

    def __init__(self, state_machine: StateMachine, ledger: Optional[Ledger] = None):
        self.state_machine = state_machine
        self.ledger = ledger
        self._candidates: dict[str, NormativeCandidateRecord] = {}
        self._active_invariants: list[str] = []

    def _generate_nca_id(self, source_document: str, location: str) -> str:
        """Generate a unique NCA-ID"""
        import hashlib
        source_hash = hashlib.md5(source_document.encode()).hexdigest()[:6]
        loc_hash = hashlib.md5(location.encode()).hexdigest()[:4]
        timestamp = datetime.now().strftime("%y%m%d%H%M%S")
        return f"NCA-{source_hash}-{loc_hash}-{timestamp}"

    def propose_candidate(
        self,
        source_document: str,
        faithful_statement: str,
        location: str,
        graph_scope: Optional[str] = None
    ) -> PINAResult:
        """
        Propose a Normative Candidate for PINA decision gate.
        """
        nca_id = self._generate_nca_id(source_document, location)

        candidate = NormativeCandidateRecord(
            nca_id=nca_id,
            source_document=source_document,
            faithful_statement=faithful_statement,
            location=location,
            graph_scope=graph_scope,
            cycle_id=self.state_machine.current_cycle.cycle_id if self.state_machine.current_cycle else None
        )

        self._candidates[nca_id] = candidate

        if self.state_machine.current_cycle:
            self.state_machine.current_cycle.nca_pending += 1

        if self.ledger:
            self.ledger.add_entry(
                entry_type=LedgerEntryType.NORMATIVE_CANDIDATE,
                content=faithful_statement,
                gf_id=nca_id,
                metadata={
                    "source": source_document,
                    "location": location,
                    "graph_scope": graph_scope,
                },
                cycle_id=candidate.cycle_id
            )

        return PINAResult(
            success=True,
            nca_id=nca_id,
            message=f"NCA {nca_id} proposed. Awaiting human decision: [A] Incorporate, [B] Do not incorporate, [C] Defer"
        )

    def decide(self, nca_id: str, decision: str) -> PINAResult:
        """
        Record the human decision for a Normative Candidate.

        Args:
            nca_id: The NCA-ID
            decision: "A" (Incorporate), "B" (Do not), or "C" (Defer)
        """
        if nca_id not in self._candidates:
            return PINAResult(
                success=False,
                nca_id=nca_id,
                message=f"NCA {nca_id} not found"
            )

        candidate = self._candidates[nca_id]

        try:
            pinadecision = PINADecision(decision.upper())
        except ValueError:
            return PINAResult(
                success=False,
                nca_id=nca_id,
                message=f"Invalid decision '{decision}'. Must be A, B, or C."
            )

        candidate.decision = pinadecision
        candidate.decided_at = datetime.now()

        if self.state_machine.current_cycle and self.state_machine.current_cycle.nca_pending > 0:
            self.state_machine.current_cycle.nca_pending -= 1

        if pinadecision == PINADecision.INCORPORATE:
            self._active_invariants.append(nca_id)
            consequence = "Rule is now an ACTIVE INVARIANT governing reasoning"
        elif pinadecision == PINADecision.DO_NOT_INCORPORATE:
            consequence = "Rule remains external text, may be discussed but cannot govern reasoning"
        else:
            consequence = "Rule remains unresolved, dependent reasoning is blocked"

        if self.ledger:
            self.ledger.add_entry(
                entry_type=LedgerEntryType.PINA_DECISION,
                content=f"PINA decision: {pinadecision.value} for {nca_id}",
                gf_id=nca_id,
                metadata={
                    "decision": pinadecision.value,
                    "consequence": consequence,
                },
                cycle_id=candidate.cycle_id
            )

        return PINAResult(
            success=True,
            nca_id=nca_id,
            message=consequence,
            decision=pinadecision.value,
            active_invariants=len(self._active_invariants)
        )

    def get_pending(self) -> list[dict]:
        """Get all pending (undecided) NCA candidates"""
        return [
            {
                "nca_id": nca_id,
                "source_document": c.source_document,
                "faithful_statement": c.faithful_statement,
                "location": c.location,
                "graph_scope": c.graph_scope,
                "created_at": c.created_at.isoformat(),
            }
            for nca_id, c in self._candidates.items()
            if c.decision is None
        ]

    def get_active_invariants(self) -> list[dict]:
        """Get all active invariants (incorporated rules)"""
        return [
            {
                "nca_id": nca_id,
                "source_document": self._candidates[nca_id].source_document,
                "faithful_statement": self._candidates[nca_id].faithful_statement,
            }
            for nca_id in self._active_invariants
            if nca_id in self._candidates
        ]

    def is_invariant(self, nca_id: str) -> bool:
        """Check if an NCA is an active invariant"""
        return nca_id in self._active_invariants

    def get_status(self) -> dict:
        """Get PINA status"""
        pending = self.get_pending()
        return {
            "pending_candidates": len(pending),
            "pending_list": pending,
            "active_invariants": len(self._active_invariants),
            "active_list": self._active_invariants,
        }