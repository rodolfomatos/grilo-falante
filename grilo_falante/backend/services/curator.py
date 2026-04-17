"""
Curator Scoring Service — Accountability scoring for curators

Implements:
- Score initialization (0.5 default)
- Penalties for incongruence
- Rewards for valid corrections
- Auto-decay for inactivity
"""

from grilo_falante.models import Curator, CuratorType
from grilo_falante.backend.db.repositories import CuratorRepository


class CuratorScoringService:
    """
    Service for managing curator accountability scores.

    Score ranges:
    - 0.9-1.0: Trusted (can validate Tier 1)
    - 0.7-0.9: Standard
    - 0.5-0.7: Provisional
    - 0.3-0.5: Probationary (needs peer review)
    - 0.0-0.3: SUSPENDED
    """

    PENALTY_AMOUNT = 0.1
    REWARD_AMOUNT = 0.05
    DECAY_AMOUNT = 0.3
    DECAY_DAYS = 180  # 6 months

    def __init__(self):
        self.curator_repo = CuratorRepository()

    async def create_curator(
        self,
        curator_key: str,
        name: str,
        curator_type: CuratorType = CuratorType.HUMAN,
        model_name: str = None,
        specializations: list[str] = None,
    ) -> Curator:
        """Create a new curator with default score."""
        curator = Curator(
            curator_key=curator_key,
            name=name,
            curator_type=curator_type,
            model_name=model_name,
            specializations=specializations or [],
            accountability_score=0.5,
        )
        return await self.curator_repo.create(curator)

    async def penalize(self, curator_id: int, reason: str = "Incongruence detected") -> Curator:
        """
        Penalize curator for incongruence.

        Decreases score by PENALTY_AMOUNT (0.1).
        """
        curator = await self.curator_repo.get_by_id(curator_id)
        if not curator:
            raise ValueError(f"Curator not found: {curator_id}")

        new_score = max(0.0, curator.accountability_score - self.PENALTY_AMOUNT)

        if new_score < curator.accountability_score:
            return await self.curator_repo.update_score(curator_id, new_score, reason)

        return curator

    async def reward(self, curator_id: int, reason: str = "Valid correction") -> Curator:
        """
        Reward curator for valid correction.

        Increases score by REWARD_AMOUNT (0.05).
        """
        curator = await self.curator_repo.get_by_id(curator_id)
        if not curator:
            raise ValueError(f"Curator not found: {curator_id}")

        new_score = min(1.0, curator.accountability_score + self.REWARD_AMOUNT)

        if new_score > curator.accountability_score:
            return await self.curator_repo.update_score(curator_id, new_score, reason)

        return curator

    async def apply_decay(self) -> int:
        """
        Apply decay to inactive curators.

        Returns count of curators affected.
        """
        return await self.curator_repo.apply_decay(self.DECAY_DAYS)

    def can_validate_tier1(self, curator: Curator) -> bool:
        """Check if curator can validate Tier 1 sources."""
        return curator.accountability_score >= 0.9

    def can_override(self, curator: Curator) -> bool:
        """Check if curator can override other curators."""
        return curator.accountability_score >= 0.5

    def needs_peer_review(self, curator: Curator) -> bool:
        """Check if curator needs peer review."""
        return curator.accountability_score < 0.5

    def is_suspended(self, curator: Curator) -> bool:
        """Check if curator is suspended."""
        return curator.accountability_score < 0.3

    def get_score_status(self, curator: Curator) -> str:
        """Get human-readable score status."""
        score = curator.accountability_score
        if score >= 0.9:
            return "Trusted Curator"
        elif score >= 0.7:
            return "Standard Curator"
        elif score >= 0.5:
            return "Provisional Curator"
        elif score >= 0.3:
            return "Probationary Curator"
        else:
            return "SUSPENDED"
