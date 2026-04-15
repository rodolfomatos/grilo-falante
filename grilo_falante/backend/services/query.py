"""
Query Pipeline Service — Full query workflow with gap detection

Implements:
1. Query parsing
2. Hybrid retrieval (vector + text)
3. Gap detection
4. Graph lint
5. Epistemic policy evaluation
6. Governance decision
"""

from dataclasses import dataclass, field
from typing import Optional

from grilo_falante.models import GovernedClaim, Gap, SessionPreferences, GMIFLevel
from grilo_falante.backend.db.repositories import ClaimRepository, GapRepository
from grilo_falante.backend.services.gap import GapDetectionService
from grilo_falante.backend.services.gmif import GMIFClassifier


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


class QueryPipeline:
    """
    Full query pipeline for epistemic governance.

    Steps:
    1. Parse query
    2. Search claims (hybrid)
    3. Detect gaps
    4. Run graph lint
    5. Evaluate policy
    6. Return decision
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

        # Step 4: Graph lint (simplified)
        lint_passed, lint_issues = self._run_lint(claims)

        # Step 5: Policy evaluation
        m4_count = sum(1 for c in claims if c.gmif_level == GMIFLevel.M4_DOUBTFUL)
        status, reason = self._evaluate_policy(claims, m4_count, lint_passed)

        # Step 6: Return result
        return QueryResult(
            status=status,
            reason=reason,
            claims=claims,
            gaps=gaps,
            m4_count=m4_count,
            lint_passed=lint_passed,
            lint_issues=lint_issues,
        )

    def _run_lint(self, claims: list[GovernedClaim]) -> tuple[bool, list[str]]:
        """
        Run graph lint on claims.

        Simplified L1-L8 checks.
        """
        issues = []

        for claim in claims:
            # L1: Check for blocking patterns
            text_lower = claim.claim_text.lower()
            if any(
                word in text_lower
                for word in ["obviously", "clearly", "just trust me"]
            ):
                issues.append(f"Blocking pattern in claim {claim.claim_key}")

            # L2: Check for unsupported generalizations
            if any(
                word in text_lower for word in ["all", "always", "never", "everyone"]
            ):
                if claim.gmif_level not in [GMIFLevel.M1_PRIMARY, GMIFLevel.M4_DOUBTFUL]:
                    issues.append(
                        f"Generalization without primary evidence: {claim.claim_key}"
                    )

            # Additional lint rules would go here...

        return len(issues) == 0, issues

    def _evaluate_policy(
        self, claims: list[GovernedClaim], m4_count: int, lint_passed: bool
    ) -> tuple[str, str]:
        """
        Evaluate epistemic policy.

        Returns:
            Tuple of (status, reason)
        """
        if not claims:
            return "blocked", "No epistemic backing available"

        if m4_count > len(claims) / 2:
            return "review", f"High proportion of doubtful claims ({m4_count}/{len(claims)})"

        if not lint_passed:
            return "review", "Lint issues detected"

        # Check for blocking claims
        blocking_claims = [
            c for c in claims if self.gmif_classifier.is_blocking(c.gmif_level, c.gmif_confidence)
        ]
        if blocking_claims:
            return "blocked", f"Blocking claims with low confidence: {len(blocking_claims)}"

        return "allowed", "Epistemic policy satisfied"
