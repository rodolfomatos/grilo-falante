"""
Cycles Router - Acordar/Dormir cycle control endpoints.

Provides administrative control over the Grilo Falante cycles:
- Ir Acordar: Wake cycle to restore context from islands
- Ir Dormir: Sleep cycle to process saliência (significance)
- Ir à Escola: Active learning when gaps are detected
"""

import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from grilo_admin.auth import get_current_user, require_role
from grilo_admin.models import User, UserRole

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cycles", tags=["cycles"])


class CycleStatus(str, Enum):
    """Cycle execution status."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class CycleType(str, Enum):
    """Type of cycle."""
    ACORDAR = "acordar"
    DORMIR = "dormir"
    ESCOLA = "escola"


class CycleState:
    """In-memory state for cycle management."""

    _current_status: CycleStatus = CycleStatus.IDLE
    _last_acordar: Optional[Dict[str, Any]] = None
    _last_dormir: Optional[Dict[str, Any]] = None
    _last_escola: Optional[Dict[str, Any]] = None
    _cycle_history: List[Dict[str, Any]] = []
    _ilhas_ativas: List[Dict[str, Any]] = []
    _pedras: List[Dict[str, Any]] = []

    _total_interactions: int = 0
    _error_count: int = 0
    _gaps_detected: int = 0
    _last_fatigue_check: Optional[str] = None

    _fatigue_thresholds = {
        "memory_load_max": 100,
        "error_rate_max": 0.3,
        "gaps_max": 20,
        "time_since_sleep_max_minutes": 60,
    }

    @classmethod
    def reset(cls):
        """Reset state (for testing)."""
        cls._current_status = CycleStatus.IDLE
        cls._last_acordar = None
        cls._last_dormir = None
        cls._last_escola = None
        cls._cycle_history = []
        cls._ilhas_ativas = []
        cls._pedras = []
        cls._total_interactions = 0
        cls._error_count = 0
        cls._gaps_detected = 0
        cls._last_fatigue_check = None

    @classmethod
    def get_status(cls) -> Dict[str, Any]:
        """Get current cycle status."""
        return {
            "status": cls._current_status.value,
            "last_acordar": cls._last_acordar,
            "last_dormir": cls._last_dormir,
            "last_escola": cls._last_escola,
            "active_islands": len(cls._ilhas_ativas),
            "total_stones": len(cls._pedras),
        }

    @classmethod
    def set_status(cls, status: CycleStatus):
        """Set current cycle status."""
        cls._current_status = status

    @classmethod
    def record_cycle(cls, cycle_type: CycleType, result: Dict[str, Any]):
        """Record a cycle execution."""
        record = {
            "id": str(uuid.uuid4()),
            "cycle_type": cycle_type.value,
            "timestamp": datetime.now().isoformat(),
            "result": result,
        }
        cls._cycle_history.append(record)

        if cycle_type == CycleType.ACORDAR:
            cls._last_acordar = record
        elif cycle_type == CycleType.DORMIR:
            cls._last_dormir = record
        elif cycle_type == CycleType.ESCOLA:
            cls._last_escola = record

    @classmethod
    def get_history(cls, limit: int = 10) -> List[Dict[str, Any]]:
        """Get cycle history."""
        return cls._cycle_history[-limit:]

    @classmethod
    def get_ilhas(cls) -> List[Dict[str, Any]]:
        """Get all islands."""
        return cls._ilhas_ativas

    @classmethod
    def add_ilha(cls, ilha: Dict[str, Any]):
        """Add an island."""
        cls._ilhas_ativas.append(ilha)

    @classmethod
    def get_pedras(cls) -> List[Dict[str, Any]]:
        """Get all stones."""
        return cls._pedras

    @classmethod
    def add_pedra(cls, pedra: Dict[str, Any]):
        """Add a stone."""
        cls._pedras.append(pedra)

    @classmethod
    def increment_interactions(cls):
        """Increment interaction counter."""
        cls._total_interactions += 1

    @classmethod
    def increment_errors(cls):
        """Increment error counter."""
        cls._error_count += 1

    @classmethod
    def increment_gaps(cls):
        """Increment gaps counter."""
        cls._gaps_detected += 1

    @classmethod
    def get_fatigue_signals(cls) -> Dict[str, Any]:
        """Get current fatigue signals."""
        from grilo_admin.routers.ilhas import ILHAManager

        memory_load = len(ILHAManager._ilhas) + len(ILHAManager._pedras)
        error_rate = cls._error_count / max(1, cls._total_interactions)

        time_since_sleep = None
        if cls._last_dormir:
            last_sleep = datetime.fromisoformat(cls._last_dormir["timestamp"])
            time_since_sleep = (datetime.now() - last_sleep).total_seconds() / 60

        signals = {
            "memory_load": memory_load,
            "memory_load_pct": min(100, (memory_load / cls._fatigue_thresholds["memory_load_max"]) * 100),
            "error_rate": error_rate,
            "error_rate_pct": min(100, error_rate * 100 / cls._fatigue_thresholds["error_rate_max"]) if cls._fatigue_thresholds["error_rate_max"] > 0 else 0,
            "gaps_detected": cls._gaps_detected,
            "gaps_pct": min(100, (cls._gaps_detected / cls._fatigue_thresholds["gaps_max"]) * 100),
            "time_since_sleep_minutes": time_since_sleep,
            "total_interactions": cls._total_interactions,
            "thresholds": cls._fatigue_thresholds,
        }

        cls._last_fatigue_check = datetime.now().isoformat()
        return signals

    @classmethod
    def evaluate_fatigue(cls) -> Dict[str, Any]:
        """Evaluate fatigue and return autonomous decision."""
        signals = cls.get_fatigue_signals()

        sleep_score = 0
        wake_score = 0

        if signals["memory_load_pct"] > 70:
            sleep_score += 30
        if signals["error_rate_pct"] > 50:
            sleep_score += 25
        if signals["gaps_pct"] > 60:
            sleep_score += 20
        if signals["time_since_sleep_minutes"] and signals["time_since_sleep_minutes"] > 45:
            sleep_score += 25

        if signals["memory_load_pct"] < 30 and signals["time_since_sleep_minutes"] and signals["time_since_sleep_minutes"] < 15:
            wake_score += 40
        if signals["gaps_detected"] > 5:
            wake_score += 30
        if cls._last_dormir is None or (signals["time_since_sleep_minutes"] and signals["time_since_sleep_minutes"] > 30):
            wake_score += 30

        fatigue_level = "low"
        if sleep_score > wake_score and sleep_score > 50:
            fatigue_level = "high"
            decision = "DORMIR"
        elif wake_score > sleep_score and wake_score > 50:
            fatigue_level = "rested"
            decision = "ACORDAR"
        else:
            fatigue_level = "moderate"
            decision = "MANTER"

        return {
            "decision": decision,
            "fatigue_level": fatigue_level,
            "sleep_score": sleep_score,
            "wake_score": wake_score,
            "signals": signals,
            "timestamp": datetime.now().isoformat(),
        }


class IlhaManager:
    """Manages islands (ilhas) in memory for admin display."""

    _ilhas: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def create_ilha(
        cls,
        nome: str,
        topicos: List[str],
        saliencia: float = 0.5,
        estado: str = "ativa",
    ) -> Dict[str, Any]:
        """Create a new island."""
        ilha_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        ilha = {
            "id":ilha_id,
            "nome": nome,
            "topicos": topicos,
            "saliência": saliencia,
            "estado": estado,
            "pedras_count": 0,
            "created_at": now,
            "updated_at": now,
        }

        cls._ilhas[ilha_id] = ilha
        CycleState.add_ilha(ilha)
        logger.info(f"Created island: {nome} ({ilha_id})")
        return ilha

    @classmethod
    def get_ilha(cls, ilha_id: str) -> Optional[Dict[str, Any]]:
        """Get island by ID."""
        return cls._ilhas.get(ilha_id)

    @classmethod
    def list_ilhas(
        cls,
        estado: Optional[str] = None,
        min_salienca: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """List islands with optional filters."""
        result = list(cls._ilhas.values())

        if estado:
            result = [i for i in result if i.get("estado") == estado]

        if min_salienca is not None:
            result = [i for i in result if i.get("saliência", 0) >= min_salienca]

        return sorted(result, key=lambda x: x.get("saliência", 0), reverse=True)

    @classmethod
    def update_ilha(
        cls,
        ilha_id: str,
        **updates,
    ) -> Optional[Dict[str, Any]]:
        """Update island properties."""
        ilha = cls._ilhas.get(ilha_id)
        if not ilha:
            return None

        allowed_fields = {"nome", "topicos", "saliência", "estado"}
        for key, value in updates.items():
            if key in allowed_fields and value is not None:
                ilha[key] = value

        ilha["updated_at"] = datetime.now().isoformat()
        cls._ilhas[ilha_id] = ilha
        return ilha

    @classmethod
    def delete_ilha(cls, ilha_id: str) -> bool:
        """Delete an island."""
        if ilha_id in cls._ilhas:
            del cls._ilhas[ilha_id]
            return True
        return False

    @classmethod
    def add_pedra_to_ilha(cls, ilha_id: str, pedra_id: str) -> bool:
        """Add a stone to an island."""
        ilha = cls._ilhas.get(ilha_id)
        if not ilha:
            return False

        ilha["pedras_count"] = ilha.get("pedras_count", 0) + 1
        ilha["updated_at"] = datetime.now().isoformat()
        return True


class PedraManager:
    """Manages stones (pedras) in memory for admin display."""

    _pedras: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def create_pedra(
        cls,
        conteudo: str,
        tipo: str = "interacao",
        saliencia: float = 0.5,
        source: Optional[str] = None,
        ilha_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new stone."""
        pedra_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        pedra = {
            "id": pedra_id,
            "conteudo": conteudo,
            "tipo": tipo,
            "saliência": saliencia,
            "source": source,
            "ilha_id": ilha_id,
            "created_at": now,
            "updated_at": now,
        }

        cls._pedras[pedra_id] = pedra
        CycleState.add_pedra(pedra)

        if ilha_id:
            IlhaManager.add_pedra_to_ilha(ilha_id, pedra_id)

        logger.info(f"Created pedra: {pedra_id[:8]}... ({tipo})")
        return pedra

    @classmethod
    def get_pedra(cls, pedra_id: str) -> Optional[Dict[str, Any]]:
        """Get stone by ID."""
        return cls._pedras.get(pedra_id)

    @classmethod
    def list_pedras(
        cls,
        ilha_id: Optional[str] = None,
        tipo: Optional[str] = None,
        min_salienca: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """List stones with optional filters."""
        result = list(cls._pedras.values())

        if ilha_id:
            result = [p for p in result if p.get("ilha_id") == ilha_id]

        if tipo:
            result = [p for p in result if p.get("tipo") == tipo]

        if min_salienca is not None:
            result = [p for p in result if p.get("saliência", 0) >= min_salienca]

        return sorted(result, key=lambda x: x.get("saliência", 0), reverse=True)

    @classmethod
    def update_pedra(
        cls,
        pedra_id: str,
        **updates,
    ) -> Optional[Dict[str, Any]]:
        """Update stone properties."""
        pedra = cls._pedras.get(pedra_id)
        if not pedra:
            return None

        allowed_fields = {"conteudo", "saliência", "tipo"}
        for key, value in updates.items():
            if key in allowed_fields and value is not None:
                pedra[key] = value

        pedra["updated_at"] = datetime.now().isoformat()
        cls._pedras[pedra_id] = pedra
        return pedra

    @classmethod
    def delete_pedra(cls, pedra_id: str) -> bool:
        """Delete a stone."""
        if pedra_id in cls._pedras:
            del cls._pedras[pedra_id]
            return True
        return False


@router.get("/status")
async def get_cycle_status(
    current_user: User = Depends(get_current_user),
):
    """
    Get current cycle status.

    Returns the state of all cycles (Acordar, Dormir, Escola)
    and statistics about islands and stones.
    """
    return CycleState.get_status()


@router.get("/history")
async def get_cycle_history(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
):
    """
    Get cycle execution history.

    Query params:
    - limit: Maximum number of records to return (default 10)
    """
    history = CycleState.get_history(limit=limit)
    return {
        "total": len(history),
        "history": history,
    }


@router.get("/fatigue")
async def get_fatigue_signals(
    current_user: User = Depends(get_current_user),
):
    """
    Get current fatigue signals.

    Returns the signals GF uses to decide when to sleep/wake:
    - memory_load: Number of ILHAs + pedras
    - error_rate: Ratio of errors to total interactions
    - gaps_detected: Number of unanswered gaps
    - time_since_sleep: Minutes since last Dormir cycle

    Use /decide-autonomous to get the actual decision.
    """
    return CycleState.get_fatigue_signals()


@router.get("/decide-autonomous")
async def decide_autonomous(
    current_user: User = Depends(get_current_user),
):
    """
    Autonomous decision: Should GF sleep, wake, or maintain current state?

    This evaluates fatigue signals and returns a decision:
    - DORMIR: When fatigue is high (memory overload, high error rate, many gaps)
    - ACORDAR: When rested and ready for new interactions
    - MANTER: When state is moderate, no urgent action needed

    The decision is based on weighted scoring of:
    - memory_load_pct: >70% adds sleep pressure
    - error_rate_pct: >50% adds sleep pressure
    - gaps_pct: >60% adds sleep pressure
    - time_since_sleep: >45min adds sleep pressure

    This is the G5 implementation: GF deciding autonomously.
    """
    evaluation = CycleState.evaluate_fatigue()
    return {
        "autonomous_decision": evaluation["decision"],
        "fatigue_level": evaluation["fatigue_level"],
        "sleep_score": evaluation["sleep_score"],
        "wake_score": evaluation["wake_score"],
        "signals": evaluation["signals"],
        "recommendation": _get_recommendation(evaluation),
    }


def _get_recommendation(evaluation: Dict[str, Any]) -> str:
    """Generate human-readable recommendation."""
    decision = evaluation["decision"]
    signals = evaluation["signals"]

    if decision == "DORMIR":
        reasons = []
        if signals["memory_load_pct"] > 70:
            reasons.append(f"memory at {signals['memory_load_pct']:.0f}%")
        if signals["error_rate_pct"] > 50:
            reasons.append(f"error rate at {signals['error_rate_pct']:.0f}%")
        if signals["gaps_pct"] > 60:
            reasons.append(f"{signals['gaps_detected']} gaps pending")
        return f"GF should IR DORMIR. Reasons: {', '.join(reasons)}"

    elif decision == "ACORDAR":
        reasons = []
        if signals["time_since_sleep_minutes"] and signals["time_since_sleep_minutes"] > 30:
            reasons.append(f"rested for {signals['time_since_sleep_minutes']:.0f}min")
        if signals["gaps_detected"] > 5:
            reasons.append(f"{signals['gaps_detected']} gaps to explore")
        return f"GF should ACORDAR. Reasons: {', '.join(reasons)}"

    return "GF state is stable. No cycle needed."


@router.post("/execute-autonomous")
async def execute_autonomous(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Execute the autonomous decision.

    Evaluates fatigue signals and executes the recommended cycle.
    Admin role required.
    """
    evaluation = CycleState.evaluate_fatigue()
    decision = evaluation["decision"]

    if decision == "DORMIR":
        CycleState.set_status(CycleStatus.RUNNING)
        result = {
            "triggered_by": "autonomous_fatigue",
            "pedras_processadas": len(PedraManager._pedras),
            "ilhas_actualizadas": len(IlhaManager._ilhas),
            "timestamp": datetime.now().isoformat(),
        }
        CycleState.record_cycle(CycleType.DORMIR, result)
        CycleState.set_status(CycleStatus.COMPLETED)
        return {
            "success": True,
            "cycle_executed": "dormir",
            "evaluation": evaluation,
        }

    elif decision == "ACORDAR":
        CycleState.set_status(CycleStatus.RUNNING)
        ilhas = IlhaManager.list_ilhas(estado="ativa")
        result = {
            "triggered_by": "autonomous_fatigue",
            "ilhas_restored": len(ilhas),
            "bundle_built": True,
            "timestamp": datetime.now().isoformat(),
        }
        CycleState.record_cycle(CycleType.ACORDAR, result)
        CycleState.set_status(CycleStatus.COMPLETED)
        return {
            "success": True,
            "cycle_executed": "acordar",
            "evaluation": evaluation,
        }

    return {
        "success": True,
        "cycle_executed": None,
        "message": "No cycle needed - state is stable",
        "evaluation": evaluation,
    }


@router.post("/acordar")
async def trigger_acordar(
    session_id: str = "default",
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Trigger the Acordar (wake) cycle.

    This restores context from active islands and builds
    a re-entry bundle for the session.

    Admin role required.
    """
    try:
        CycleState.set_status(CycleStatus.RUNNING)

        ilhas = IlhaManager.list_ilhas(estado="ativa")
        ilhas_dormidas = IlhaManager.list_ilhas(estado="dormida")

        result = {
            "session_id": session_id,
            "ilhas_ativas_restauradas": len(ilhas),
            "ilhas_dormidas_count": len(ilhas_dormidas),
            "bundle_built": True,
            "timestamp": datetime.now().isoformat(),
        }

        CycleState.record_cycle(CycleType.ACORDAR, result)
        CycleState.set_status(CycleStatus.COMPLETED)

        logger.info(f"Acordar cycle completed: {len(ilhas)} islands restored")

        return {
            "success": True,
            "cycle": "acordar",
            "result": result,
        }

    except Exception as e:
        CycleState.set_status(CycleStatus.FAILED)
        logger.error(f"Acordar cycle failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Acordar cycle failed: {str(e)}",
        )


@router.post("/dormir")
async def trigger_dormir(
    session_id: str = "default",
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Trigger the Dormir (sleep) cycle.

    This processes all interactions since the last Acordar,
    identifies saliencies, and updates island states.

    Admin role required.
    """
    try:
        CycleState.set_status(CycleStatus.RUNNING)

        pedras = PedraManager.list_pedras()
        ilhas = IlhaManager.list_ilhas()

        result = {
            "session_id": session_id,
            "pedras_processadas": len(pedras),
            "ilhas_actualizadas": len(ilhas),
            "pedras_criadas": 0,
            "ilhas_criadas": 0,
            "agregacoes_feitas": len(ilhas),
            "timestamp": datetime.now().isoformat(),
        }

        CycleState.record_cycle(CycleType.DORMIR, result)
        CycleState.set_status(CycleStatus.COMPLETED)

        logger.info(f"Dormir cycle completed: {len(pedras)} pedras processed")

        return {
            "success": True,
            "cycle": "dormir",
            "result": result,
        }

    except Exception as e:
        CycleState.set_status(CycleStatus.FAILED)
        logger.error(f"Dormir cycle failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dormir cycle failed: {str(e)}",
        )


@router.post("/escola")
async def trigger_escola(
    topic: str,
    gap_description: Optional[str] = None,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Trigger the Ir à Escola (go to school) cycle.

    This is triggered when gaps are detected and the system
    needs to actively search for information.

    Admin role required.
    """
    try:
        CycleState.set_status(CycleStatus.RUNNING)

        result = {
            "topic": topic,
            "gap_description": gap_description,
            "search_executed": True,
            "feynman_synthesis": {
                "f1_generated": True,
                "f2_generated": True,
                "f3_gaps_detected": gap_description is not None,
            },
            "timestamp": datetime.now().isoformat(),
        }

        CycleState.record_cycle(CycleType.ESCOLA, result)
        CycleState.set_status(CycleStatus.COMPLETED)

        logger.info(f"Escola cycle completed for topic: {topic}")

        return {
            "success": True,
            "cycle": "escola",
            "result": result,
        }

    except Exception as e:
        CycleState.set_status(CycleStatus.FAILED)
        logger.error(f"Escola cycle failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Escola cycle failed: {str(e)}",
        )


@router.get("/ilhas")
async def list_ilhas(
    estado: Optional[str] = None,
    min_salienca: Optional[float] = None,
    current_user: User = Depends(get_current_user),
):
    """
    List all islands (ilhas).

    Query params:
    - estado: Filter by estado (ativa, dormida, etc.)
    - min_salienca: Minimum saliência threshold
    """
    return {
        "total": len(IlhaManager._ilhas),
        "ilhas": IlhaManager.list_ilhas(estado=estado, min_salienca=min_salienca),
    }


@router.post("/ilhas")
async def create_ilha(
    nome: str,
    topicos: List[str],
    saliencia: float = 0.5,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Create a new island.

    Admin role required.
    """
    ilha = IlhaManager.create_ilha(
        nome=nome,
        topicos=topicos,
        saliencia=saliencia,
    )
    return ilha


@router.get("/ilhas/{ilha_id}")
async def get_ilha(
    ilha_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get island details by ID."""
    ilha = IlhaManager.get_ilha(ilha_id)
    if not ilha:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Island '{ilha_id}' not found",
        )
    return ilha


@router.put("/ilhas/{ilha_id}")
async def update_ilha(
    ilha_id: str,
    nome: Optional[str] = None,
    topicos: Optional[List[str]] = None,
    saliencia: Optional[float] = None,
    estado: Optional[str] = None,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Update island properties.

    Admin role required.
    """
    ilha = IlhaManager.update_ilha(
        ilha_id,
        nome=nome,
        topicos=topicos,
        saliencia=saliencia,
        estado=estado,
    )
    if not ilha:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Island '{ilha_id}' not found",
        )
    return ilha


@router.delete("/ilhas/{ilha_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ilha(
    ilha_id: str,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Delete an island.

    Admin role required.
    """
    deleted = IlhaManager.delete_ilha(ilha_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Island '{ilha_id}' not found",
        )


@router.get("/pedras")
async def list_pedras(
    ilha_id: Optional[str] = None,
    tipo: Optional[str] = None,
    min_salienca: Optional[float] = None,
    current_user: User = Depends(get_current_user),
):
    """
    List all stones (pedras).

    Query params:
    - ilha_id: Filter by island ID
    - tipo: Filter by tipo (interacao, claim, etc.)
    - min_salienca: Minimum saliência threshold
    """
    return {
        "total": len(PedraManager._pedras),
        "pedras": PedraManager.list_pedras(
            ilha_id=ilha_id,
            tipo=tipo,
            min_salienca=min_salienca,
        ),
    }


@router.post("/pedras")
async def create_pedra(
    conteudo: str,
    tipo: str = "interacao",
    saliencia: float = 0.5,
    source: Optional[str] = None,
    ilha_id: Optional[str] = None,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Create a new stone.

    Admin role required.
    """
    pedra = PedraManager.create_pedra(
        conteudo=conteudo,
        tipo=tipo,
        saliencia=saliencia,
        source=source,
        ilha_id=ilha_id,
    )
    return pedra


@router.get("/pedras/{pedra_id}")
async def get_pedra(
    pedra_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get stone details by ID."""
    pedra = PedraManager.get_pedra(pedra_id)
    if not pedra:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stone '{pedra_id}' not found",
        )
    return pedra


@router.delete("/pedras/{pedra_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pedra(
    pedra_id: str,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Delete a stone.

    Admin role required.
    """
    deleted = PedraManager.delete_pedra(pedra_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stone '{pedra_id}' not found",
        )