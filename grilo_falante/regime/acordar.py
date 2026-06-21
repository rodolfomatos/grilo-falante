"""
Grilo Falante ACORDAR — Wake-up Ritual

ACORDAR activates the regime with temporal anchoring and intention declaration.
Transitions: LOADED → ACTIVE → GOVERNING

Principle: temporal anchor MUST come from an external source (OS clock, NTP).
The model cannot infer what time it is — it must verify externally.

VAI_DORMIR hibernates the regime.
Transitions: GOVERNING → HIBERNATED
"""

import logging
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from .state import StateMachine, CycleState
from .ledger import Ledger, LedgerEntryType

logger = logging.getLogger(__name__)


@dataclass
class GitContext:
    branch: str = ""
    commit_hash: str = ""
    commit_message: str = ""
    dirty: bool = False
    error: Optional[str] = None


@dataclass
class IslandContext:
    active_count: int = 0
    dormant_count: int = 0
    bundle: Optional[dict] = None
    error: Optional[str] = None


@dataclass
class AcordarResult:
    success: bool
    message: str
    temporal_anchor: Optional[str] = None
    intention_declared: Optional[str] = None
    source: str = ""
    verified_timestamp: Optional[str] = None
    git: Optional[dict] = None
    islands: Optional[dict] = None
    anchor_mismatch: bool = False
    warnings: list[str] = field(default_factory=list)


def _get_system_time() -> str:
    """Get current system time as ISO string."""
    return datetime.now().isoformat()


def _get_git_context(path: Optional[str] = None) -> GitContext:
    """Get git context from current or specified repo."""
    ctx = GitContext()
    try:
        cwd = path or "."
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=5, cwd=cwd,
        )
        if result.returncode == 0:
            ctx.branch = result.stdout.strip()
        else:
            ctx.error = "Not a git repository"
            return ctx

        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5, cwd=cwd,
        )
        if result.returncode == 0:
            ctx.commit_hash = result.stdout.strip()

        result = subprocess.run(
            ["git", "log", "-1", "--pretty=format:%s"],
            capture_output=True, text=True, timeout=5, cwd=cwd,
        )
        if result.returncode == 0:
            ctx.commit_message = result.stdout.strip()

        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, timeout=5, cwd=cwd,
        )
        if result.returncode == 0:
            ctx.dirty = bool(result.stdout.strip())

    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        ctx.error = str(e)

    return ctx


async def _get_island_context(session_id: str = "mcp") -> IslandContext:
    """Restore island context from DB."""
    ctx = IslandContext()
    try:
        from app.regime.acordar import acordar as legacy_acordar

        resultado = await legacy_acordar(session_id=session_id)
        ctx.active_count = len(resultado.ilhas_ativas)
        ctx.dormant_count = len(resultado.ilhas_dormintes)
        ctx.bundle = resultado.bundle
    except Exception as e:
        ctx.error = str(e)
        logger.warning(f"Island restoration skipped: {e}")

    return ctx


class Acordar:
    """
    ACORDAR - Wake-up ritual for the Grilo Falante regime.

    The regime is only active after:
    1. Temporal anchoring (verified from external source)
    2. Intention explicitly declared
    3. Context restored (islands, git)

    Without all three, the cycle has no epistemic anchor.
    """

    def __init__(self, state_machine: StateMachine, ledger: Optional[Ledger] = None):
        self.state_machine = state_machine
        self.ledger = ledger

    def execute(
        self,
        intention: str,
        temporal_anchor: Optional[str] = None,
        mode: str = "exploratory",
        use_external_time: bool = True,
        session_id: str = "mcp",
    ) -> AcordarResult:
        """
        Execute the ACORDAR ritual.

        The temporal anchor ALWAYS comes from the system clock (external source).
        If a human-supplied anchor is provided, both are recorded and
        any discrepancy is flagged.

        Args:
            intention: What the human intends to accomplish
            temporal_anchor: Optional human-supplied anchor for cross-reference
            mode: "exploratory" or "committed"
            use_external_time: Get time from system clock (always True effectively)
            session_id: Session ID for island restoration

        Returns:
            AcordarResult with success status, verified anchor, context
        """
        if self.state_machine.current_cycle is None:
            return AcordarResult(
                success=False, message="No active cycle. Execute grilo_load first."
            )

        ctx = self.state_machine.current_cycle

        if not intention or not intention.strip():
            return AcordarResult(success=False, message="Intention declaration is required")

        warnings: list[str] = []

        # Step 1: Get external time
        system_time = _get_system_time()
        verified_anchor = system_time

        if temporal_anchor and temporal_anchor.strip():
            anchor_str = temporal_anchor.strip()
            if anchor_str != system_time[:len(anchor_str)]:
                warnings.append(
                    f"Temporal anchor mismatch: declared '{anchor_str}', "
                    f"system clock says '{system_time}'"
                )
        else:
            temporal_anchor = system_time

        # Step 2: Get git context
        git_ctx = _get_git_context()
        if git_ctx.error:
            warnings.append(f"Git context unavailable: {git_ctx.error}")

        # Step 3: Get island context
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            island_ctx = loop.run_until_complete(_get_island_context(session_id))
            loop.close()
        except Exception:
            island_ctx = IslandContext()

        # Step 4: Set state machine
        self.state_machine.set_temporal_anchor(verified_anchor)
        self.state_machine.set_intention(intention)
        self.state_machine.set_exploratory(mode == "exploratory")

        if not self.state_machine.activate():
            return AcordarResult(
                success=False, message=f"Failed to transition from {ctx.state.value} to ACTIVE"
            )

        if not self.state_machine.govern():
            return AcordarResult(success=False, message="Failed to transition to GOVERNING state")

        ctx = self.state_machine.current_cycle

        if self.ledger:
            self.ledger.add_entry(
                entry_type=LedgerEntryType.REGIME_EVENT,
                content=f"ACORDAR executed: anchor={verified_anchor}, intention={intention}, mode={mode}",
                metadata={
                    "temporal_anchor": verified_anchor,
                    "intention": intention,
                    "mode": mode,
                    "cycle_id": ctx.cycle_id,
                    "git_branch": git_ctx.branch,
                    "git_commit": git_ctx.commit_hash,
                    "islands_active": island_ctx.active_count,
                    "warnings": warnings,
                },
                cycle_id=ctx.cycle_id,
            )

        return AcordarResult(
            success=True,
            message="ACORDAR completed. Regime is now governing.",
            temporal_anchor=verified_anchor,
            intention_declared=intention,
            source="system_clock",
            verified_timestamp=system_time,
            git={
                "branch": git_ctx.branch,
                "commit": git_ctx.commit_hash,
                "message": git_ctx.commit_message,
                "dirty": git_ctx.dirty,
                "error": git_ctx.error,
            },
            islands={
                "active_count": island_ctx.active_count,
                "dormant_count": island_ctx.dormant_count,
                "bundle": island_ctx.bundle,
                "error": island_ctx.error,
            },
            anchor_mismatch=temporal_anchor != system_time[:len(temporal_anchor)]
            if temporal_anchor else False,
            warnings=warnings,
        )

    async def vai_dormir_async(
        self,
        session_id: str = "mcp",
        handoff_dir: Optional[str] = None,
        collect_interactions: bool = True,
    ) -> dict:
        """
        VAI_DORMIR async - Hibernate the regime AND execute sleep cycle.

        This performs the complete sleep cycle:
        1. Collect cycle state (claims, NCAs, governance records)
        2. Write handoff file for continuity
        3. Execute island batch processing (memory consolidation)
        4. Generate sleep report with cycle summary
        5. Hibernate the regime

        Only after all steps does it hibernate.
        """
        if self.state_machine.current_cycle is None:
            return {"success": False, "message": "No active cycle"}

        ctx = self.state_machine.current_cycle

        relatório = {
            "success": False,
            "message": "",
            "cycle_id": ctx.cycle_id,
            "passos_executados": [],
            "handoff_path": None,
            "cycle_summary": {},
            "island_result": {},
        }

        # Step 1: Collect cycle state
        cycle_summary = {
            "cycle_id": ctx.cycle_id,
            "state": ctx.state.value,
            "temporal_anchor": ctx.temporal_anchor,
            "intention": ctx.intention,
            "claims_count": ctx.claims_count,
            "nca_pending": ctx.nca_pending,
            "is_exploratory": ctx.is_exploratory,
            "git_branch": None,
            "git_commit": None,
        }
        git_ctx = _get_git_context()
        if not git_ctx.error:
            cycle_summary["git_branch"] = git_ctx.branch
            cycle_summary["git_commit"] = git_ctx.commit_hash
            cycle_summary["git_dirty"] = git_ctx.dirty

        relatório["cycle_summary"] = cycle_summary
        relatório["passos_executados"].append("COLETAR_ESTADO")

        # Step 2: Write handoff file
        handoff_base = Path(handoff_dir or "aes/handoffs")
        handoff_base.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        handoff_path = handoff_base / f"{timestamp}-{ctx.cycle_id}.md"

        handoff_lines = [
            f"# Handoff: {ctx.cycle_id}",
            f"Date: {datetime.now().isoformat()}",
            f"State: {ctx.state.value}",
            f"Intention: {ctx.intention or '(not declared)'}",
            f"Temporal Anchor: {ctx.temporal_anchor or '(not set)'}",
            f"Claims: {ctx.claims_count}",
            f"NCAs Pending: {ctx.nca_pending}",
            f"Mode: {'exploratory' if ctx.is_exploratory else 'committed'}",
            f"Git: {cycle_summary.get('git_branch', 'N/A')} @ {cycle_summary.get('git_commit', 'N/A')}",
            "",
            "## Open Items",
            "_(populate with decisions taken, pending items, what does not carry over)_",
            "",
            "## Knowledge State",
            "_(summarize what was learned, what remains uncertain)_",
            "",
        ]
        if ctx.ledger_entry_ids:
            handoff_lines.append("## Ledger Entries")
            for eid in ctx.ledger_entry_ids:
                handoff_lines.append(f"- {eid}")
            handoff_lines.append("")

        handoff_path.write_text("\n".join(handoff_lines))
        relatório["handoff_path"] = str(handoff_path)
        relatório["passos_executados"].append("HANDOFF")

        # Step 3: Island batch processing
        interactions = []
        if collect_interactions:
            interactions = self._coletar_interações_do_dia()

        try:
            from app.regime.dormir import ProcessadorBatch

            processador = ProcessadorBatch()
            island_result = await processador.executar(
                session_id=session_id,
                interações=interactions,
            )
            relatório["island_result"] = island_result
            relatório["passos_executados"].append("ILHAS")
        except Exception as e:
            logger.warning(f"Island processing failed: {e}")
            relatório["island_result"] = {"error": str(e)}

        # Step 4: Generate sleep report
        relatório["passos_executados"].append("RELATÓRIO")

        # Step 5: Hibernate
        if not self.state_machine.hibernate():
            relatório["success"] = False
            relatório["message"] = "Cannot hibernate from current state"
            return relatório

        if self.ledger:
            self.ledger.add_entry(
                entry_type=LedgerEntryType.REGIME_EVENT,
                content=f"VAI_DORMIR: Regime hibernated. Handoff: {handoff_path.name}",
                metadata={
                    "cycle_id": ctx.cycle_id,
                    "handoff": str(handoff_path),
                    "claims_count": ctx.claims_count,
                    "steps": relatório.get("passos_executados", []),
                },
                cycle_id=ctx.cycle_id,
            )

        relatório["success"] = True
        relatório["message"] = (
            f"Regime hibernated. Handoff saved to {handoff_path}. "
            "Use grilo_resume to continue."
        )

        return relatório

    def vai_dormir(self, handoff_dir: Optional[str] = None) -> dict:
        """
        VAI_DORMIR sync - Write handoff and hibernate.

        For full sleep cycle with batch processing, use vai_dormir_async().
        """
        if self.state_machine.current_cycle is None:
            return {"success": False, "message": "No active cycle"}

        ctx = self.state_machine.current_cycle

        # Write handoff
        handoff_path = None
        handoff_base = Path(handoff_dir or "aes/handoffs")
        handoff_base.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        hf_path = handoff_base / f"{timestamp}-{ctx.cycle_id}-sync.md"
        hf_path.write_text(
            f"# Handoff: {ctx.cycle_id}\n"
            f"Date: {datetime.now().isoformat()}\n"
            f"State: {ctx.state.value}\n"
            f"Intention: {ctx.intention or '(not declared)'}\n"
            f"Temporal Anchor: {ctx.temporal_anchor or '(not set)'}\n"
            f"Claims: {ctx.claims_count}\n"
            f"Mode: {'exploratory' if ctx.is_exploratory else 'committed'}\n"
        )
        handoff_path = str(hf_path)

        if not self.state_machine.hibernate():
            return {"success": False, "message": "Cannot hibernate from current state"}

        if self.ledger:
            self.ledger.add_entry(
                entry_type=LedgerEntryType.REGIME_EVENT,
                content=f"VAI_DORMIR: Regime hibernated (sync). Handoff: {hf_path.name}",
                metadata={"cycle_id": ctx.cycle_id, "handoff": handoff_path},
                cycle_id=ctx.cycle_id,
            )

        return {
            "success": True,
            "message": f"Regime hibernated. Handoff saved to {handoff_path}. Use vai_dormir_async() for full sleep cycle.",
            "handoff_path": handoff_path,
        }

    def _coletar_interações_do_dia(self) -> list:
        """
        Collect interactions since last wake.

        Returns list of interaction dicts for the sleep cycle.
        Currently returns empty list — full collection requires
        ChatShell integration that records each message.
        """
        return []

    def resume(self, handoff_dir: Optional[str] = None) -> dict:
        """
        Resume from hibernation, optionally reading latest handoff.

        Args:
            handoff_dir: Optional handoff directory to read context

        Returns:
            Status dict with resume result
        """
        if not self.state_machine.resume():
            return {"success": False, "message": "Cannot resume from current state"}

        ctx = self.state_machine.current_cycle

        # Try to read latest handoff for context
        handoff_content = None
        if handoff_dir:
            handoff_base = Path(handoff_dir)
            handoffs = sorted(handoff_base.glob(f"*{ctx.cycle_id}*.md"), reverse=True)
            if handoffs:
                handoff_content = handoffs[0].read_text()

        if self.ledger:
            self.ledger.add_entry(
                entry_type=LedgerEntryType.REGIME_EVENT,
                content="ACORDAR (resume): Regime resumed",
                metadata={
                    "cycle_id": ctx.cycle_id,
                    "handoff_found": handoff_content is not None,
                },
                cycle_id=ctx.cycle_id,
            )

        return {
            "success": True,
            "message": "Regime resumed and governing.",
            "handoff_restored": handoff_content is not None,
            "handoff_content": handoff_content if handoff_content else None,
        }

    def get_status(self) -> dict:
        """Get ACORDAR status"""
        ctx = self.state_machine.current_cycle
        return {
            "temporal_anchor_declared": ctx.temporal_anchor is not None if ctx else False,
            "temporal_anchor": ctx.temporal_anchor if ctx else None,
            "source": "system_clock" if ctx and ctx.temporal_anchor else None,
            "intention_declared": ctx.intention is not None if ctx else False,
            "intention": ctx.intention if ctx else None,
            "is_exploratory": ctx.is_exploratory if ctx else None,
        }
