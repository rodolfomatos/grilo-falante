"""
Gap Detection Service — Knowledge gap identification

Implements three types of gaps:
- TIPO A: Research Failure (no claims with sufficient score)
- TIPO B: Confidence Mismatch (info without trackable provenance)
- TIPO C: Explicit Uncertainty (cannot explain at child's level)
"""

from dataclasses import dataclass
from typing import Optional

from grilo_falante.models import Gap, GapStatus, GapType, GovernedClaim, GMIFLevel
from grilo_falante.backend.db.repositories import GapRepository, ClaimRepository


@dataclass
class GapDetectionResult:
    """Result of gap detection."""

    gap_found: bool
    gap_type: Optional[GapType]
    gap_reason: Optional[str]
    existing_claims: list[GovernedClaim]
    suggested_threshold: float


class GapDetectionService:
    """
    Service for detecting knowledge gaps.

    Uses three detection strategies:
    - TIPO A: Query returns no claims with score >= threshold
    - TIPO B: Query returns claims but none with provenance
    - TIPO C: Cannot generate FEP-1 explanation
    """

    DEFAULT_THRESHOLD = 0.5
    M4_THRESHOLD = 0.3

    def __init__(self):
        self.gap_repo = GapRepository()
        self.claim_repo = ClaimRepository()

    async def detect_gaps(
        self,
        query: str,
        session_id: Optional[str] = None,
        threshold: float = DEFAULT_THRESHOLD,
    ) -> GapDetectionResult:
        """
        Detect gaps for a query.

        Args:
            query: The query to check
            session_id: Session for filtering
            threshold: Evidence threshold (default 0.5)

        Returns:
            GapDetectionResult with gap info and existing claims
        """
        # Search for existing claims
        claims = await self.claim_repo.search(query, session_id, limit=20)

        if not claims:
            # TIPO A: No claims found
            return GapDetectionResult(
                gap_found=True,
                gap_type=GapType.TIPO_A_FAILURE,
                gap_reason=f"No claims found for query: {query}",
                existing_claims=[],
                suggested_threshold=threshold,
            )

        # Check for M4 claims with low confidence
        m4_claims = [c for c in claims if c.gmif_level == GMIFLevel.M4_DOUBTFUL]
        high_conf_claims = [c for c in claims if c.gmif_confidence >= threshold]

        if not high_conf_claims and m4_claims:
            # TIPO A: Claims exist but none meet threshold
            return GapDetectionResult(
                gap_found=True,
                gap_type=GapType.TIPO_A_FAILURE,
                gap_reason="Claims found but none meet confidence threshold",
                existing_claims=claims,
                suggested_threshold=threshold,
            )

        # Check provenance
        no_provenance = [c for c in claims if not c.provenance]
        if no_provenance and len(no_provenance) == len(claims):
            # TIPO B: No provenance
            return GapDetectionResult(
                gap_found=True,
                gap_type=GapType.TIPO_B_MISMATCH,
                gap_reason="Claims found but none have trackable provenance",
                existing_claims=claims,
                suggested_threshold=threshold,
            )

        # Check if can explain at child level
        if await self._cannot_explain_child(query, claims):
            # TIPO C: Explicit uncertainty
            return GapDetectionResult(
                gap_found=True,
                gap_type=GapType.TIPO_C_EXPLICIT,
                gap_reason="Cannot generate simple explanation",
                existing_claims=claims,
                suggested_threshold=threshold,
            )

        # No gap detected
        return GapDetectionResult(
            gap_found=False,
            gap_type=None,
            gap_reason=None,
            existing_claims=claims,
            suggested_threshold=threshold,
        )

    async def create_gap(
        self,
        query: str,
        gap_type: GapType,
        reason: str,
        session_id: Optional[str] = None,
    ) -> Gap:
        """
        Create a new gap record.

        Args:
            query: Original query
            gap_type: Type of gap
            reason: Why it's a gap
            session_id: Session context

        Returns:
            Created Gap
        """
        from grilo_falante.backend.db.repositories import generate_key

        gap = Gap(
            gap_key=generate_key("gap"),
            gap_type=gap_type,
            query=query,
            reason=reason,
            session_id=session_id or "global",
        )
        return await self.gap_repo.create(gap)

    async def _cannot_explain_child(self, query: str, claims: list[GovernedClaim]) -> bool:
        """
        Check if cannot explain at child level.

        Simplified: checks if claims are too complex.
        """
        # Simplified: if most claims are M4 or have low confidence
        if not claims:
            return True

        low_conf_count = sum(1 for c in claims if c.gmif_confidence < 0.4)
        return low_conf_count > len(claims) / 2
