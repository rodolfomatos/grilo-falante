"""
Grilo Falante LOADER — Cycle Management

The LOADER activates the Grilo Falante regime in a cycle.
Transitions: INACTIVE → LOADED

Enhanced with explicit LOAD act pattern from prototype:
- Requires explicit "LOAD GriloFalante FROM system.md" command
- Generates SystemUseRecord traces for audit trail
- Resolves authoritative artefacts from KERNEL.md
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List

from .state import StateMachine, CycleContext, CycleState
from .ledger import Ledger, LedgerEntryType


@dataclass
class LoadResult:
    success: bool
    message: str
    cycle_id: Optional[str] = None
    state: Optional[str] = None
    blocked: bool = False
    block_reason: Optional[str] = None
    authoritative_artefacts: Optional[Dict[str, List[str]]] = None
    use_records: Optional[List[Dict]] = None
    error: Optional[str] = None


@dataclass
class SystemUseRecord:
    """Record of artefact usage for governance audit trail."""
    artefact_type: str = "Objeto Digital"
    record_type: str = "SystemUseRecord"
    source: str = ""
    context: str = ""
    effect: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "artefact_type": self.artefact_type,
            "record_type": self.record_type,
            "source": self.source,
            "context": self.context,
            "effect": self.effect,
            "timestamp": self.timestamp,
        }


class Loader:
    """
    LOADER implementation - activates the Grilo Falante regime in a cycle.

    The LOADER transforms aggregated documents into operational governance
    instruments and enforces materialization rules.

    Enhanced with explicit LOAD act pattern:
    - Command must be exactly: "LOAD GriloFalante FROM system.md"
    - Generates SystemUseRecord traces
    - Resolves authoritative artefacts from KERNEL.md
    """

    VALID_LOAD_COMMAND = "LOAD GriloFalante FROM system.md"

    def __init__(
        self,
        ledger: Optional[Ledger] = None,
        system_path: Optional[Path] = None,
        kernel_path: Optional[Path] = None
    ):
        self.state_machine = StateMachine()
        self.ledger = ledger
        self.system_path = system_path or Path("system.md")
        self.kernel_path = kernel_path or Path("regime/regime.md")
        self.use_records: List[SystemUseRecord] = []
        self._initialized = False

    def initialize(self) -> bool:
        """Initialize the loader"""
        if self._initialized:
            return True
        self._initialized = True
        return True

    def load(self, command: str = VALID_LOAD_COMMAND) -> LoadResult:
        """
        Execute the LOAD command to activate the regime.

        Args:
            command: Must be exactly "LOAD GriloFalante FROM system.md"

        Returns:
            LoadResult with success status and details
        """
        normalized = self._normalize_command(command)

        if normalized != self.VALID_LOAD_COMMAND:
            return LoadResult(
                success=False,
                message="Invalid LOAD act",
                blocked=True,
                block_reason="invalid_load_act",
                error=f"Expected: '{self.VALID_LOAD_COMMAND}', Got: '{command}'"
            )

        if not self._initialized:
            self.initialize()

        if self.state_machine.current_cycle is None:
            ctx = self.state_machine.start_cycle()
        else:
            ctx = self.state_machine.current_cycle
            if ctx.state == CycleState.LOADED:
                pass
            elif not self.state_machine.load():
                return LoadResult(
                    success=False,
                    message="Failed to transition to LOADED state",
                    state=ctx.state.value,
                    blocked=True,
                    block_reason="state_transition_failed"
                )

        ctx = self.state_machine.current_cycle

        authoritative = self._resolve_kernel_authority()
        self._materialize_use(
            source="regime.md",
            context="Explicit activation of governed cycle",
            effect="Regime became operational through explicit LOAD act"
        )
        self._materialize_use(
            source="LOADER",
            context="Authority resolution for current governed cycle",
            effect="Operational authority resolved to kernel-listed artefacts"
        )

        if self.ledger:
            self.ledger.add_entry(
                entry_type=LedgerEntryType.REGIME_EVENT,
                content=f"Regime loaded: v3.0 (explicit LOAD act)",
                entry_id=f"LOAD-{datetime.now().strftime('%y%m%d%H%M%S')}",
                cycle_id=ctx.cycle_id
            )

        return LoadResult(
            success=True,
            message="Grilo Falante v3.0 loaded successfully",
            cycle_id=ctx.cycle_id,
            state=ctx.state.value,
            blocked=False,
            authoritative_artefacts=authoritative,
            use_records=[r.to_dict() for r in self.use_records]
        )

    def unload(self) -> LoadResult:
        """Unload the regime (end cycle)"""
        if self.state_machine.current_cycle is None:
            return LoadResult(success=False, message="No active cycle")

        ctx = self.state_machine.current_cycle
        self.state_machine.end_cycle()

        self._materialize_use(
            source="LOADER",
            context="Explicit deactivation",
            effect="Regime cycle terminated"
        )

        if self.ledger:
            self.ledger.add_entry(
                entry_type=LedgerEntryType.REGIME_EVENT,
                content="Regime unloaded",
                cycle_id=ctx.cycle_id
            )

        return LoadResult(success=True, message="Regime unloaded")

    def get_status(self) -> dict:
        """Get current regime status"""
        status = self.state_machine.get_status()

        if self.ledger:
            status["ledger_stats"] = self.ledger.get_stats()

        status["use_records_count"] = len(self.use_records)

        return status

    def _normalize_command(self, command: str) -> str:
        """Normalize LOAD command."""
        command = command.strip()
        return command

    def _materialize_use(
        self,
        source: str,
        context: str,
        effect: str,
        artefact_type: str = "Objeto Digital"
    ) -> SystemUseRecord:
        """Record artefact usage for audit trail."""
        record = SystemUseRecord(
            artefact_type=artefact_type,
            source=source,
            context=context,
            effect=effect
        )
        self.use_records.append(record)
        return record

    def _resolve_kernel_authority(self) -> Dict[str, List[str]]:
        """Resolve authoritative artefacts from regime.md."""
        if not self.kernel_path.exists():
            return {
                "constitutional_layer": [],
                "execution_pipeline": [],
                "epistemic_graph_infrastructure": [],
                "validation_mechanisms": [],
            }

        content = self.kernel_path.read_text()
        sections: Dict[str, List[str]] = {}
        current_section: Optional[str] = None

        for raw_line in content.splitlines():
            line = raw_line.strip()
            if line.startswith("#"):
                section_match = re.match(r"#+\s+(.+)", line)
                if section_match:
                    current_section = section_match.group(1)
                    sections.setdefault(current_section, [])
            elif current_section and line.startswith("-"):
                item = line.lstrip("- ").strip()
                if item:
                    sections[current_section].append(item)

        return {
            "constitutional_layer": sections.get("Constitutional Layer", []),
            "execution_pipeline": sections.get("Execution Pipeline", []),
            "epistemic_graph_infrastructure": sections.get("Epistemic Graph Infrastructure", []),
            "validation_mechanisms": sections.get("Validation Mechanisms", []),
        }

    def materialize_graph_use(
        self,
        graph_name: str,
        state: str,
        transition: str
    ) -> Dict:
        """Record graph usage for audit trail."""
        record = self._materialize_use(
            source=graph_name,
            context=f"State={state}",
            effect=f"Validated transition={transition}"
        )
        return record.to_dict()