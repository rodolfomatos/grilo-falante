"""
Governance Services — Epistemic governance layer

Provides:
- GovernanceLayer: Block/Allow/Review decisions
- TransitionValidator: Claim state machine
- EpistemicPolicy: Policy evaluation
- EpistemicAlignment: LLM vs Evidence validation
- QueryClassifier: Query type classification
- FalsifiabilityLint: Popperian falsification principles
- LoopClosure: Open loop management
- ConstraintLayer: Discursive constraint enforcement
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
from grilo_falante.backend.services.governance.epistemic_objects import (
    PropositionRole,
    RelationType,
    TensionType,
    TensionResolution,
    LoopStatus,
    LoopCriticality,
    ClosureType,
    FalsificationStatus,
    ArtefactType,
    FalsificationCondition,
    Proposition,
    PropositionDependency,
    TensionRecord,
    OpenLoop,
    ClosureRecord,
    TrustedCommitment,
    Artefact,
)
from grilo_falante.backend.services.governance.falsifiability_lint import (
    LintResult,
    run_proposition_lint,
    check_foundational_boundaries,
    check_derived_support,
    evaluate_lint_for_promotion,
)
from grilo_falante.backend.services.governance.loop_closure import (
    generate_loop_id,
    open_loop_from_claim,
    open_loop_from_proposition,
    open_loop_from_tension,
    close_loop,
    suspend_loop,
    block_loop,
    register_trusted_commitment,
    can_promote,
    evaluate_loops_for_promotion,
    apply_closure_policy,
    get_loops_by_criticality,
    get_open_critical_loops,
    get_loop_summary,
    summarize_closure_state,
    create_loops_from_tensions,
)
from grilo_falante.backend.services.governance.constraint_layer import (
    ConstraintType,
    ConstraintLevel,
    Constraint,
    ConstraintViolation,
    create_default_constraints,
    evaluate_text_constraints,
    evaluate_for_promotion,
    get_constraint_summary,
)

__all__ = [
    # Governance Layer
    "GovernanceDecision",
    "governance",
    "governance_with_blocking",
    "verify_claims",
    # Transition
    "TransitionError",
    "ClaimTransitionContext",
    "validate_transition",
    "is_valid_transition",
    "get_allowed_transitions",
    "is_terminal_state",
    "requires_audit",
    "VALID_STATES",
    # Policy
    "evaluate_epistemic_policy",
    "POLICY",
    # Alignment
    "EpistemicAlignment",
    "AlignmentResult",
    "AlignedClaim",
    "classify_claim_evidence_pair",
    # Query
    "QueryType",
    "classify_query",
    "requires_evidence",
    "allows_speculation",
    # Epistemic Objects
    "PropositionRole",
    "PropositionLegitimacy",
    "RelationType",
    "TensionType",
    "TensionResolution",
    "LoopStatus",
    "LoopCriticality",
    "ClosureType",
    "FalsificationStatus",
    "ArtefactType",
    "FalsificationCondition",
    "Proposition",
    "PropositionDependency",
    "TensionRecord",
    "OpenLoop",
    "ClosureRecord",
    "TrustedCommitment",
    "Artefact",
    # Falsifiability Lint
    "LintResult",
    "run_proposition_lint",
    "check_foundational_boundaries",
    "check_derived_support",
    "evaluate_lint_for_promotion",
    # Loop Closure
    "generate_loop_id",
    "open_loop_from_claim",
    "open_loop_from_proposition",
    "open_loop_from_tension",
    "close_loop",
    "suspend_loop",
    "block_loop",
    "register_trusted_commitment",
    "can_promote",
    "evaluate_loops_for_promotion",
    "apply_closure_policy",
    "get_loops_by_criticality",
    "get_open_critical_loops",
    "get_loop_summary",
    "summarize_closure_state",
    "create_loops_from_tensions",
    # Constraint Layer
    "ConstraintType",
    "ConstraintLevel",
    "Constraint",
    "ConstraintViolation",
    "create_default_constraints",
    "evaluate_text_constraints",
    "evaluate_for_promotion",
    "get_constraint_summary",
]
