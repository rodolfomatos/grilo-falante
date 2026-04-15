from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from models.epistemic_objects import (
    OpenLoop,
    ClosureRecord,
    TrustedCommitment,
    LoopStatus,
    LoopCriticality,
    ClosureType,
    TensionRecord,
    Proposition,
)


def generate_loop_id() -> str:
    return f"LOOP-{datetime.now().strftime('%y%m%d')}-{uuid.uuid4().hex[:6]}"


def open_loop_from_claim(
    claim_id: str,
    claim_text: str,
    criticality: LoopCriticality = LoopCriticality.MEDIUM
) -> OpenLoop:
    return OpenLoop(
        id=generate_loop_id(),
        source_type="claim",
        source_id=claim_id,
        status=LoopStatus.OPEN,
        criticality=criticality,
        closure_policy="claim_validation",
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )


def open_loop_from_proposition(
    proposition: Proposition,
    criticality: LoopCriticality = LoopCriticality.MEDIUM
) -> OpenLoop:
    return OpenLoop(
        id=generate_loop_id(),
        source_type="proposition",
        source_id=proposition.id,
        status=LoopStatus.OPEN,
        criticality=criticality,
        closure_policy="proposition_validation",
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )


def open_loop_from_tension(
    tension: TensionRecord,
    criticality: Optional[LoopCriticality] = None
) -> OpenLoop:
    if criticality is None:
        if tension.severity >= 3:
            criticality = LoopCriticality.HIGH
        elif tension.severity >= 2:
            criticality = LoopCriticality.MEDIUM
        else:
            criticality = LoopCriticality.LOW
    
    return OpenLoop(
        id=generate_loop_id(),
        source_type="tension",
        source_id=tension.id,
        status=LoopStatus.OPEN,
        criticality=criticality,
        closure_policy="tension_resolution",
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )


def close_loop(
    loop: OpenLoop,
    closure_type: ClosureType,
    evidence: Optional[str] = None
) -> ClosureRecord:
    loop.status = LoopStatus.CLOSED
    loop.updated_at = datetime.now().isoformat()
    
    return ClosureRecord(
        loop_id=loop.id,
        closure_type=closure_type,
        evidence=evidence,
        closed_at=datetime.now().isoformat()
    )


def suspend_loop(loop: OpenLoop, reason: str) -> ClosureRecord:
    loop.status = LoopStatus.SUSPENDED
    loop.updated_at = datetime.now().isoformat()
    
    return ClosureRecord(
        loop_id=loop.id,
        closure_type=ClosureType.SUSPENSION,
        evidence=reason,
        closed_at=datetime.now().isoformat()
    )


def block_loop(loop: OpenLoop, reason: str) -> ClosureRecord:
    loop.status = LoopStatus.BLOCKED
    loop.updated_at = datetime.now().isoformat()
    
    return ClosureRecord(
        loop_id=loop.id,
        closure_type=ClosureType.BLOCKED,
        evidence=reason,
        closed_at=datetime.now().isoformat()
    )


def register_trusted_commitment(
    loop: OpenLoop,
    commitment_text: str,
    committed_by: str,
    materialization: str
) -> TrustedCommitment:
    loop.trusted_commitment = {
        "text": commitment_text,
        "committed_by": committed_by,
        "materialization": materialization
    }
    loop.status = LoopStatus.SCHEDULED
    loop.updated_at = datetime.now().isoformat()
    
    return TrustedCommitment(
        id=f"TC-{uuid.uuid4().hex[:6]}",
        claim_id=loop.source_id,
        commitment_text=commitment_text,
        materialization=materialization,
        committed_by=committed_by,
        created_at=datetime.now().isoformat()
    )


def can_promote(loops: List[OpenLoop]) -> tuple[bool, List[str]]:
    blocked_loops = [l for l in loops if l.status == LoopStatus.OPEN and l.criticality == LoopCriticality.HIGH]
    
    if blocked_loops:
        reasons = [f"Critical loop open: {l.id}" for l in blocked_loops]
        return False, reasons
    
    return True, []


def get_loop_summary(loops: List[OpenLoop]) -> Dict[str, Any]:
    return {
        "total": len(loops),
        "open": len([l for l in loops if l.status == LoopStatus.OPEN]),
        "scheduled": len([l for l in loops if l.status == LoopStatus.SCHEDULED]),
        "suspended": len([l for l in loops if l.status == LoopStatus.SUSPENDED]),
        "blocked": len([l for l in loops if l.status == LoopStatus.BLOCKED]),
        "closed": len([l for l in loops if l.status == LoopStatus.CLOSED]),
        "promoted": len([l for l in loops if l.status == LoopStatus.PROMOTED]),
        "critical_high": len([l for l in loops if l.criticality == LoopCriticality.HIGH]),
        "critical_medium": len([l for l in loops if l.criticality == LoopCriticality.MEDIUM]),
        "critical_low": len([l for l in loops if l.criticality == LoopCriticality.LOW]),
    }


def create_loops_from_tensions(tensions: List[TensionRecord]) -> List[OpenLoop]:
    loops = []
    for tension in tensions:
        if tension.resolution_status != TensionResolution.RESOLVED:
            loop = open_loop_from_tension(tension)
            loops.append(loop)
    return loops