"""Services package — Business logic for Grilo Falante"""

from grilo_falante.backend.services.gfid import GFIDService
from grilo_falante.backend.services.gmif import GMIFClassifier
from grilo_falante.backend.services.feynman import FeynmanService
from grilo_falante.backend.services.gap import GapDetectionService
from grilo_falante.backend.services.curator import CuratorScoringService
from grilo_falante.backend.services.query import QueryPipeline
from grilo_falante.backend.services.school import SchoolModeService
from grilo_falante.backend.services.lint import CognitiveLint, LintState
from grilo_falante.backend.services.why_loop import WhyLoopService, WhyLoopResult
from grilo_falante.backend.services.active_search import ActiveSearchService, SearchResult
from grilo_falante.backend.services.utils import (
    TimeoutError as GriloTimeoutError,
    RetryResult,
    with_timeout,
    with_retry,
    retry_operation,
    export_html,
)
from grilo_falante.backend.services.governance import (
    governance,
    governance_with_blocking,
    verify_claims,
    GovernanceDecision,
    TransitionError,
    validate_transition,
    is_valid_transition,
    get_allowed_transitions,
    is_terminal_state,
    requires_audit,
    VALID_STATES,
    evaluate_epistemic_policy,
    POLICY,
    EpistemicAlignment,
    AlignmentResult,
    AlignedClaim,
    classify_claim_evidence_pair,
    QueryType,
    classify_query,
    requires_evidence,
    allows_speculation,
)

__all__ = [
    "GFIDService",
    "GMIFClassifier",
    "FeynmanService",
    "GapDetectionService",
    "CuratorScoringService",
    "QueryPipeline",
    "SchoolModeService",
    "CognitiveLint",
    "LintState",
    "WhyLoopService",
    "WhyLoopResult",
    "ActiveSearchService",
    "SearchResult",
    "GriloTimeoutError",
    "RetryResult",
    "with_timeout",
    "with_retry",
    "retry_operation",
    "export_html",
    "governance",
    "governance_with_blocking",
    "verify_claims",
    "GovernanceDecision",
    "TransitionError",
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