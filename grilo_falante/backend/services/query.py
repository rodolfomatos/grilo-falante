"""
Query Pipeline Service — Full query workflow with gap detection

Implements:
1. Query parsing
2. Hybrid retrieval (vector + text)
3. Gap detection
4. Graph lint (using governance services)
5. Epistemic policy evaluation (using governance services)
6. Governance decision (using governance_layer)
"""

from dataclasses import dataclass, field
from typing import Optional

from grilo_falante.models import GovernedClaim, Gap, SessionPreferences, GMIFLevel
from grilo_falante.backend.db.repositories import ClaimRepository, GapRepository
from grilo_falante.backend.services.gap import GapDetectionService
from grilo_falante.backend.services.gmif import GMIFClassifier
from grilo_falante.backend.services.governance import (
    governance,
    governance_with_blocking,
    evaluate_text_constraints,
    evaluate_lint_for_promotion,
)
from grilo_falante.backend.services.governance.epistemic_objects import (
    Proposition,
    PropositionRole,
    PropositionLegitimacy,
)


@dataclass
class QueryResult:
    """Result of query pipeline."""

    status: str  # allowed, blocked, review
    reason: str
    claims: list[GovernedClaim]
    gaps: list[Gap]
    m4_count: int
    lint_passed: bool
    lint_issues: list[str] = field(default_factory=list)
    governance_decision: dict = field(default_factory=dict)


class QueryPipeline:
    """
    Full query pipeline for epistemic governance.

    Steps:
    1. Parse query
    2. Search claims (hybrid)
    3. Detect gaps
    4. Run graph lint (using governance constraint_layer)
    5. Evaluate policy (using governance falsifiability_lint)
    6. Governance decision (using governance_layer)
    """

    def __init__(self):
        self.claim_repo = ClaimRepository()
        self.gap_service = GapDetectionService()
        self.gmif_classifier = GMIFClassifier()

    async def execute(
        self,
        query: str,
        session_id: str = "default",
        auto_school_mode: bool = True,
        threshold: float = 0.5,
    ) -> QueryResult:
        """
        Execute full query pipeline.

        Args:
            query: The query to process
            session_id: Session for filtering
            auto_school_mode: Whether to auto-create gaps
            threshold: Evidence threshold

        Returns:
            QueryResult with decision and claims
        """
        # Step 1-2: Search claims
        claims = await self.claim_repo.search(query, session_id, limit=20)

        # Step 3: Detect gaps
        gap_result = await self.gap_service.detect_gaps(
            query, session_id, threshold
        )

        gaps = []
        if gap_result.gap_found and auto_school_mode:
            # Create gap record
            gap = await self.gap_service.create_gap(
                query=query,
                gap_type=gap_result.gap_type,
                reason=gap_result.gap_reason,
                session_id=session_id,
            )
            gaps.append(gap)

        # Step 4: Run lint using governance constraint_layer
        lint_passed, lint_issues = self._run_governance_lint(claims)

        # Step 5: Run governance policy evaluation
        m4_count = sum(1 for c in claims if c.gmif_level == GMIFLevel.M4_DOUBTFUL)

        # Step 6: Get governance decision using governance_layer
        gov_decision = governance(
            claims=self._claims_to_dict(claims),
            query=query,
        )

        status = gov_decision.decision
        reason = gov_decision.reason

        # Return result
        return QueryResult(
            status=status,
            reason=reason,
            claims=claims,
            gaps=gaps,
            m4_count=m4_count,
            lint_passed=lint_passed,
            lint_issues=lint_issues,
            governance_decision=gov_decision.details,
        )

    def _claims_to_dict(self, claims: list[GovernedClaim]) -> list[dict]:
        """Convert claims to dict format for governance service."""
        return [
            {
                "id": c.claim_key,
                "claim_text": c.claim_text,
                "gmif_type": c.gmif_level.value if c.gmif_level else "M3",
                "score": c.gmif_confidence or 0.5,
                "source_id": c.source_id,
            }
            for c in claims
        ]

    def _run_governance_lint(self, claims: list[GovernedClaim]) -> tuple[bool, list[str]]:
        """
        Run graph lint using governance constraint_layer.

        Uses the real constraint evaluation from constraint_layer.py.
        """
        issues = []

        for claim in claims:
            text = claim.claim_text

            # Run constraint evaluation
            passed, violations = evaluate_text_constraints(text)

            if not passed:
                for v in violations:
                    issues.append(f"Constraint {v.constraint_id}: {v.message}")

            # Check for blocking patterns
            text_lower = text.lower()
            blocking_patterns = ["obviously", "clearly", "just trust me", "believe me"]
            if any(word in text_lower for word in blocking_patterns):
                issues.append(f"Blocking pattern in claim {claim.claim_key}")

            # Check for unsupported generalizations
            if any(word in text_lower for word in ["all", "always", "never", "everyone"]):
                if claim.gmif_level not in [GMIFLevel.M1_PRIMARY, GMIFLevel.M4_DOUBTFUL]:
                    issues.append(
                        f"Generalization without primary evidence: {claim.claim_key}"
                    )

        return len(issues) == 0, issues
