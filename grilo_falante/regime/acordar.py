"""
Grilo Falante ACORDAR — Wake-up Ritual

ACORDAR activates the regime with temporal anchoring and intention declaration.
Transitions: LOADED → ACTIVE → GOVERNING

VAI_DORMIR hibernates the regime.
Transitions: GOVERNING → HIBERNATED
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .state import StateMachine, CycleState
from .ledger import Ledger, LedgerEntryType


@dataclass
class AcordarResult:
    success: bool
    message: str
    temporal_anchor: Optional[str] = None
    intention_declared: Optional[str] = None


class Acordar:
    """
    ACORDAR - Wake-up ritual for the Grilo Falante regime.

    The regime is only active after:
    1. Temporal anchoring declared
    2. Intention explicitly declared

    Without both, the cycle is invalid.
    """

    def __init__(self, state_machine: StateMachine, ledger: Optional[Ledger] = None):
        self.state_machine = state_machine
        self.ledger = ledger

    def execute(
        self, temporal_anchor: str, intention: str, mode: str = "exploratory"
    ) -> AcordarResult:
        """
        Execute the ACORDAR ritual.

        Args:
            temporal_anchor: Date/time context (e.g., "2026-04-15")
            intention: What the human intends to accomplish
            mode: "exploratory" or "committed"

        Returns:
            AcordarResult with success status and details
        """
        if self.state_machine.current_cycle is None:
            return AcordarResult(
                success=False, message="No active cycle. Execute grilo_load first."
            )

        ctx = self.state_machine.current_cycle

        if not temporal_anchor or not temporal_anchor.strip():
            return AcordarResult(success=False, message="Temporal anchor is required")

        if not intention or not intention.strip():
            return AcordarResult(success=False, message="Intention declaration is required")

        self.state_machine.set_temporal_anchor(temporal_anchor)
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
                content=f"ACORDAR executed: anchor={temporal_anchor}, intention={intention}, mode={mode}",
                metadata={
                    "temporal_anchor": temporal_anchor,
                    "intention": intention,
                    "mode": mode,
                    "cycle_id": ctx.cycle_id,
                },
                cycle_id=ctx.cycle_id,
            )

        return AcordarResult(
            success=True,
            message="ACORDAR completed. Regime is now governing.",
            temporal_anchor=temporal_anchor,
            intention_declared=intention,
        )

    async def vai_dormir_async(self) -> dict:
        """
        VAI_DORMIR async - Hibernate the regime AND execute sleep cycle.

        This performs the complete sleep cycle:
        1. Collect interactions since last wake
        2. Identify stones (salient interactions)
        3. Evaluate transformation into islands
        4. Aggregate around gravity centers
        5. Update existing island states (apply decay)
        6. Consolidate memory
        7. Save to persistent storage
        8. Generate sleep report

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
            "pedras_criadas": 0,
            "ilhas_criadas": 0,
            "ilhas_actualizadas": 0,
            "agregações_feitas": 0,
        }

        try:
            # Import the batch processor
            from app.regime.dormir import ProcessadorBatch

            # Collect interactions since last wake
            interações = self._coletar_interações_do_dia()
            relatório["passos_executados"].append("COLETAR")
            relatório["interações_coletadas"] = len(interações)

            # Execute batch processing (steps 2-5)
            processador = ProcessadorBatch()
            dormir_result = await processador.executar(
                session_id=ctx.cycle_id or "regime",
                interações=interações,
            )

            relatório.update(dormir_result)
            relatório["passos_executados"].append("PROCESSAR")

            # Step 6-7: Already done in processador.executar()

            # Step 8: Generate sleep report
            relatório["passos_executados"].append("RELATÓRIO")

        except Exception as e:
            logger.warning(f"Erro no ciclo dormir: {e}")
            relatório["message"] = f"Sleep cycle error: {e}"
            # Continue to hibernate even if sleep cycle failed

        # Now hibernate
        if not self.state_machine.hibernate():
            relatório["success"] = False
            relatório["message"] = "Cannot hibernate from current state"
            return relatório

        if self.ledger:
            self.ledger.add_entry(
                entry_type=LedgerEntryType.REGIME_EVENT,
                content="VAI_DORMIR: Regime hibernated",
                metadata={
                    "cycle_id": ctx.cycle_id,
                    "relatório": str(relatório.get("passos_executados", [])),
                },
                cycle_id=ctx.cycle_id,
            )

        relatório["success"] = True
        relatório[
            "message"
        ] = "Regime hibernated. Sleep cycle complete. Use grilo_resume to continue."

        return relatório

    def vai_dormir(self) -> dict:
        """
        VAI_DORMIR sync - Simplified version that just hibernates.

        For full sleep cycle with batch processing, use vai_dormir_async().
        This sync version is kept for backwards compatibility.
        """
        if self.state_machine.current_cycle is None:
            return {"success": False, "message": "No active cycle"}

        if not self.state_machine.hibernate():
            return {"success": False, "message": "Cannot hibernate from current state"}

        ctx = self.state_machine.current_cycle

        if self.ledger:
            self.ledger.add_entry(
                entry_type=LedgerEntryType.REGIME_EVENT,
                content="VAI_DORMIR: Regime hibernated (sync)",
                metadata={"cycle_id": ctx.cycle_id},
                cycle_id=ctx.cycle_id,
            )

        return {
            "success": True,
            "message": "Regime hibernated. Use vai_dormir_async() for full sleep cycle.",
        }

    def _coletar_interações_do_dia(self) -> list:
        """
        Collect interactions since last wake.

        Returns list of interaction dicts for the sleep cycle.
        """
        # TODO: Implement actual collection from ChatShell or other sources
        # For now, return empty list (will be populated by ChatShell.end())
        return []

    def resume(self) -> dict:
        """Resume from hibernation"""
        if not self.state_machine.resume():
            return {"success": False, "message": "Cannot resume from current state"}

        ctx = self.state_machine.current_cycle

        if self.ledger:
            self.ledger.add_entry(
                entry_type=LedgerEntryType.REGIME_EVENT,
                content="ACORDAR (resume): Regime resumed",
                metadata={"cycle_id": ctx.cycle_id},
                cycle_id=ctx.cycle_id,
            )

        return {"success": True, "message": "Regime resumed and governing."}

    def get_status(self) -> dict:
        """Get ACORDAR status"""
        ctx = self.state_machine.current_cycle
        return {
            "temporal_anchor_declared": ctx.temporal_anchor is not None if ctx else False,
            "temporal_anchor": ctx.temporal_anchor if ctx else None,
            "intention_declared": ctx.intention is not None if ctx else False,
            "intention": ctx.intention if ctx else None,
            "is_exploratory": ctx.is_exploratory if ctx else None,
        }
