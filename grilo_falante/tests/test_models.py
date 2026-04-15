"""Tests for models"""

import pytest
from grilo_falante.models import (
    GovernedClaim,
    Gap,
    Curator,
    GMIFLevel,
    GapStatus,
    CuratorType,
)


def test_claim_to_card():
    """Test claim to card conversion."""
    claim = GovernedClaim(
        claim_key="test:1",
        claim_text="Test claim",
        gmif_level=GMIFLevel.M1_PRIMARY,
        gmif_confidence=0.9,
    )
    card = claim.to_card()
    assert card["claim_key"] == "test:1"
    assert card["gmif_level"] == "M1"


def test_curator_score_boundaries():
    """Test curator score boundaries."""
    curator = Curator(
        curator_key="curator:1",
        name="Test Curator",
        accountability_score=0.95,
    )
    assert curator.can_validate_tier1 is True
    assert curator.is_suspended is False

    curator.accountability_score = 0.2
    assert curator.is_suspended is True
    assert curator.can_validate_tier1 is False


def test_gap_status():
    """Test gap status transitions."""
    gap = Gap(
        gap_key="gap:1",
        query="test query",
        reason="no evidence",
    )
    assert gap.is_resolved is False
    assert gap.status == GapStatus.IDENTIFIED
