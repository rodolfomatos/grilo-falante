from typing import List, Dict, Any, Optional, Tuple
from models.epistemic_objects import (
    OpenLoop,
    ClosureRecord,
    TrustedCommitment,
    LoopStatus,
    LoopCriticality,
    ClosureType,
)
from reasoning.open_loops import (
    close_loop,
    suspend_loop,
    block_loop,
    register_trusted_commitment,
    can_promote,
)


def evaluate_loops_for_promotion(
    loops: List[OpenLoop],
    trusted_commitments: Optional[List[TrustedCommitment]] = None
) -> Tuple[str, List[str]]:
    can_promote_flag, reasons = can_promote(loops)
    
    if not can_promote_flag:
        return "BLOCK", reasons
    
    open_loops = [l for l in loops if l.status == LoopStatus.OPEN]
    if open_loops:
        return "CONDITIONAL", [f"Open loops: {len(open_loops)}"]
    
    return "PASS", []


def apply_closure_policy(
    loop: OpenLoop,
    policy: str,
    evidence: Optional[str] = None,
    committed_by: Optional[str] = None
) -> ClosureRecord:
    if policy == "evidence_based":
        return close_loop(loop, ClosureType.EVIDENCE_BASED, evidence)
    
    elif policy == "trusted_commitment":
        if not committed_by:
            raise ValueError("committed_by required for trusted_commitment policy")
        
        commitment = register_trusted_commitment(
            loop,
            commitment_text=evidence or "",
            committed_by=committed_by,
            materialization="materialized"
        )
        return close_loop(loop, ClosureType.TRUSTED_COMMITMENT, evidence)
    
    elif policy == "suspension":
        return suspend_loop(loop, evidence or "suspended")
    
    elif policy == "block":
        return block_loop(loop, evidence or "blocked")
    
    else:
        return close_loop(loop, ClosureType.EVIDENCE_BASED, evidence or "default closure")


def get_loops_by_criticality(loops: List[OpenLoop]) -> Dict[str, List[OpenLoop]]:
    return {
        "high": [l for l in loops if l.criticality == LoopCriticality.HIGH],
        "medium": [l for l in loops if l.criticality == LoopCriticality.MEDIUM],
        "low": [l for l in loops if l.criticality == LoopCriticality.LOW],
    }


def get_open_critical_loops(loops: List[OpenLoop]) -> List[OpenLoop]:
    return [
        l for l in loops
        if l.status == LoopStatus.OPEN and l.criticality == LoopCriticality.HIGH
    ]


def summarize_closure_state(
    loops: List[OpenLoop],
    closures: List[ClosureRecord]
) -> Dict[str, Any]:
    loop_summary = {
        "total": len(loops),
        "open": len([l for l in loops if l.status == LoopStatus.OPEN]),
        "closed": len([l for l in loops if l.status == LoopStatus.CLOSED]),
        "suspended": len([l for l in loops if l.status == LoopStatus.SUSPENDED]),
        "blocked": len([l for l in loops if l.status == LoopStatus.BLOCKED]),
    }
    
    closure_summary = {
        "total": len(closures),
        "evidence_based": len([c for c in closures if c.closure_type == ClosureType.EVIDENCE_BASED]),
        "trusted_commitment": len([c for c in closures if c.closure_type == ClosureType.TRUSTED_COMMITMENT]),
        "suspension": len([c for c in closures if c.closure_type == ClosureType.SUSPENSION]),
        "blocked": len([c for c in closures if c.closure_type == ClosureType.BLOCKED]),
    }
    
    return {
        "loops": loop_summary,
        "closures": closure_summary,
        "can_promote": can_promote(loops)[0]
    }