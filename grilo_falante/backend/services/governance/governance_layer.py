"""
Governance Layer — Epistemic governance decisions

Implements decision logic for block/allow/review based on:
- Evidence quality
- GMIF classification
- Graph integrity
- Epistemic policy
"""

from dataclasses import dataclass
from typing import Optional

from grilo_falante.config import settings
from grilo_falante.backend.services.governance.epistemic_policy import (
    evaluate_epistemic_policy,
    POLICY,
)


@dataclass
class GovernanceDecision:
    decision: str
    reason: str
    details: dict


def _count_m4_nodes(gmif_graph) -> int:
    if not gmif_graph:
        return 0
    count = 0
    for _, data in gmif_graph.nodes(data=True) if hasattr(gmif_graph, "nodes") else []:
        if data.get("gmif_type") == "M4":
            count += 1
    return count


def _get_decision_reason(
    decision: str, claims: list, m4_count: int, has_structure: bool, scores: list
) -> str:
    if decision == "block":
        if not claims:
            return "no_claims_retrieved"
        avg_score = sum(scores) / len(scores) if scores else 0
        if avg_score < 0.15:
            return "claim_scores_too_low"
        return "insufficient_evidence"

    if decision == "review":
        return f"doubtful_testimony_m4_count_{m4_count}"

    if decision == "allow":
        if has_structure:
            return "epistemic_policy_approved"
        return "sufficient_evidence"

    return "unknown"


def verify_claims(claims, threshold: float = None) -> list:
    """
    Soft filtering of claims - keeps all above threshold.
    If none pass, returns best available claim.
    """
    if not claims:
        return []

    threshold = threshold or POLICY["evidence_threshold"]

    strong = [c for c in claims if c.get("score", 0) >= threshold]

    if strong:
        return strong

    if claims:
        best = max(claims, key=lambda x: x.get("score", 0))
        return [best]

    return []


def governance(
    claims: list,
    query: Optional[str] = None,
    gmif_graph=None,
    lint: Optional[dict] = None,
    fragility: Optional[list] = None,
    contradictions: Optional[list] = None,
    tension_map: Optional[dict] = None,
    consensus: Optional[list] = None,
    return_explanation: bool = True,
) -> GovernanceDecision:
    """
    Make governance decision about whether to allow/block/review a query response.

    Args:
        claims: List of retrieved claims
        query: Original query (optional)
        gmif_graph: GMIF analysis graph (optional)
        lint: Linting results (optional)
        fragility: Fragility analysis (optional)
        contradictions: Contradiction detection results (optional)
        tension_map: Tension analysis (optional)
        consensus: Consensus analysis (optional)
        return_explanation: If True, return GovernanceDecision

    Returns:
        GovernanceDecision with decision, reason, and details
    """
    if not claims:
        return GovernanceDecision(
            decision="block",
            reason="no_claims_retrieved",
            details={"claims_count": 0, "m4_count": 0, "has_structure": False},
        )

    m4_count = _count_m4_nodes(gmif_graph)

    has_structure = any([lint, fragility, contradictions, consensus])

    if m4_count > 0:
        return GovernanceDecision(
            decision="review",
            reason=f"doubtful_testimony_m4_count_{m4_count}",
            details={
                "claims_count": len(claims),
                "m4_count": m4_count,
                "has_structure": has_structure,
            },
        )

    if has_structure:
        decision, epl_reason = evaluate_epistemic_policy(
            claims=claims,
            lint=lint,
            fragility=fragility,
            contradictions=contradictions,
            tension_map=tension_map,
            consensus=consensus,
        )
        return GovernanceDecision(
            decision=decision,
            reason=f"epl: {epl_reason}",
            details={
                "claims_count": len(claims),
                "m4_count": m4_count,
                "has_structure": has_structure,
                "factors": [f"epl: {epl_reason}"],
            },
        )

    scores = [c.get("score", 0) for c in claims]
    best = max(scores)

    sources = set(c.get("source_id") for c in claims if c.get("source_id"))

    if len(claims) == 1:
        decision = "allow" if best >= 0.2 else "block"
    else:
        if best < 0.2:
            decision = "block"
        elif len(sources) < 1:
            decision = "block"
        else:
            decision = "allow"

    return GovernanceDecision(
        decision=decision,
        reason=_get_decision_reason(decision, claims, m4_count, has_structure, scores),
        details={
            "claims_count": len(claims),
            "avg_score": sum(scores) / len(scores) if scores else 0,
            "max_score": max(scores) if scores else 0,
            "m4_count": m4_count,
            "has_structure": has_structure,
        },
    )


def governance_with_blocking(
    claims: list,
    query: Optional[str] = None,
    gmif_graph=None,
    lint: Optional[dict] = None,
    **kwargs,
) -> tuple[str, GovernanceDecision]:
    """
    Governance decision with automatic blocking if M4 threshold exceeded.

    Returns:
        tuple: (should_block: bool, decision: GovernanceDecision)
    """
    decision = governance(claims, query, gmif_graph, lint, **kwargs)

    should_block = False

    if decision.decision == "block":
        should_block = True
    elif decision.decision == "review":
        m4_count = _count_m4_nodes(gmif_graph)
        if m4_count > 0:
            avg_score = decision.details.get("avg_score", 0)
            if avg_score < settings.m4_block_threshold:
                should_block = True

    return should_block, decision
