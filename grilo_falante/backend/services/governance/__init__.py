"""
Governance Services — Epistemic governance layer

Provides:
- GovernanceLayer: Block/Allow/Review decisions
- TransitionValidator: Claim state machine
- EpistemicPolicy: Policy evaluation
- EpistemicAlignment: LLM vs Evidence validation
- QueryClassifier: Query type classification
"""

from grilo_falante.backend.services.governance.governance_layer import (
    GovernanceDecision,
    governance,
    governance_with_blocking,
    verify_claims,
)
from grilo_falante.backend.services.governance.transition_validator import (
    TransitionError,
    ClaimTransitionContext,
    validate_transition,
    is_valid_transition,
    get_allowed_transitions,
    is_terminal_state,
    requires_audit,
    VALID_STATES,
)
from grilo_falante.backend.services.governance.epistemic_policy import (
    evaluate_epistemic_policy,
    POLICY,
)
from grilo_falante.backend.services.governance.alignment import (
    EpistemicAlignment,
    AlignmentResult,
    AlignedClaim,
    classify_claim_evidence_pair,
)
from grilo_falante.backend.services.governance.query_classifier import (
    QueryType,
    classify_query,
    requires_evidence,
    allows_speculation,
)

__all__ = [
    "GovernanceDecision",
    "governance",
    "governance_with_blocking",
    "verify_claims",
    "TransitionError",
    "ClaimTransitionContext",
    "validate_transition",
    "is_valid_transition",
    "get_allowed_transitions",
    "is_terminal_state",
    "requires_audit",
    "VALID_STATES",
    "evaluate_epistemic_policy",
    "POLICY",
    "EpistemicAlignment",
    "AlignmentResult",
    "AlignedClaim",
    "classify_claim_evidence_pair",
    "QueryType",
    "classify_query",
    "requires_evidence",
    "allows_speculation",
]
