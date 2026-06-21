"""Shared test fixtures for Grilo Falante v3.0 tests."""

from datetime import datetime
from typing import Any

import pytest

from grilo_falante.models import (
    GMIFLevel,
    Gap,
    GapStatus,
    GovernedClaim,
    SourceTier,
    StudyPlan,
    StudyPlanStep,
)


@pytest.fixture
def sample_claims() -> list[GovernedClaim]:
    """A curated set of claims for epistemic lint testing."""
    return [
        GovernedClaim(
            claim_key="c:sea_level",
            claim_text="Global sea levels have risen approximately 20cm since 1900",
            gmif_level=GMIFLevel.VERIFIED,
            gmif_confidence=0.92,
            claim_references=[],
            provenance={"source": "IPCC AR6", "references": []},
            created_at=datetime(2024, 1, 1),
        ),
        GovernedClaim(
            claim_key="c:co2_temp",
            claim_text="CO2 concentrations correlate with global temperature rise",
            gmif_level=GMIFLevel.DERIVED,
            gmif_confidence=0.85,
            claim_references=["c:sea_level"],
            provenance={"source": "Derived from IPCC data", "references": ["c:sea_level"]},
            created_at=datetime(2024, 2, 1),
        ),
        GovernedClaim(
            claim_key="c:temp_rise",
            claim_text="Global temperature has risen 1.1°C since 1880",
            gmif_level=GMIFLevel.VERIFIED,
            gmif_confidence=0.90,
            claim_references=[],
            provenance={"source": "NOAA", "references": []},
            created_at=datetime(2024, 1, 15),
        ),
        GovernedClaim(
            claim_key="c:temp_no_rise",
            claim_text="Global temperature has NOT risen significantly since 1880",
            gmif_level=GMIFLevel.CONFLICTED,
            gmif_confidence=0.30,
            claim_references=[],
            provenance={"source": "Unknown blog", "references": []},
            created_at=datetime(2024, 3, 1),
        ),
        GovernedClaim(
            claim_key="c:policy",
            claim_text="Carbon pricing is the most effective climate policy",
            gmif_level=GMIFLevel.CONCLUSION,
            gmif_confidence=0.75,
            claim_references=["c:co2_temp", "c:temp_rise"],
            provenance={"references": ["c:co2_temp", "c:temp_rise"]},
            created_at=datetime(2024, 3, 15),
        ),
        GovernedClaim(
            claim_key="c:bad_conclusion",
            claim_text="Climate change is a hoax based on flawed models",
            gmif_level=GMIFLevel.CONCLUSION,
            gmif_confidence=0.15,
            claim_references=["c:temp_no_rise"],
            provenance={"references": ["c:temp_no_rise"]},
            created_at=datetime(2024, 4, 1),
        ),
        GovernedClaim(
            claim_key="c:orphan_claim",
            claim_text="Some unconnected observation",
            gmif_level=GMIFLevel.UNVERIFIED,
            gmif_confidence=0.10,
            claim_references=[],
            provenance={},
            created_at=datetime(2024, 4, 15),
        ),
        GovernedClaim(
            claim_key="c:self_ref",
            claim_text="This claim references itself",
            gmif_level=GMIFLevel.INTERPRETATION,
            gmif_confidence=0.50,
            claim_references=["c:self_ref"],
            provenance={"references": ["c:self_ref"]},
            created_at=datetime(2024, 5, 1),
        ),
        GovernedClaim(
            claim_key="c:too_confident",
            claim_text="Derived claim with excessive confidence",
            gmif_level=GMIFLevel.DERIVED,
            gmif_confidence=0.99,
            claim_references=["c:sea_level"],
            provenance={"references": ["c:sea_level"]},
            created_at=datetime(2024, 5, 15),
        ),
        GovernedClaim(
            claim_key="c:anachronism",
            claim_text="Claim that references via provenance a future claim",
            gmif_level=GMIFLevel.SYNTHESIS,
            gmif_confidence=0.60,
            claim_references=[],
            provenance={"references": ["c:future_claim"]},
            created_at=datetime(2024, 1, 1),
        ),
    ]


@pytest.fixture
def sample_gaps() -> list[Gap]:
    return [
        Gap(
            gap_key="gap:g:1",
            query="Missing sea level acceleration data — Need post-2020 sea level data",
            reason="Post-2020 sea level data not yet analysed in existing claims",
            status=GapStatus.IDENTIFIED,
        ),
        Gap(
            gap_key="gap:g:2",
            query="Unclear policy effectiveness metrics — Need metrics to evaluate carbon pricing",
            reason="Carbon pricing impact metrics are not available in current knowledge base",
            status=GapStatus.IN_PROGRESS,
        ),
    ]


@pytest.fixture
def sample_study_plan() -> StudyPlan:
    return StudyPlan(
        plan_key="plan:test",
        gap_key="gap:g:1",
        topic="Sea Level Rise Analysis",
        steps=[
            StudyPlanStep(order=1, description="Review IPCC AR6", resources=["ipcc_ar6.pdf"],
                          estimated_time="30 min"),
            StudyPlanStep(order=2, description="Analyse recent trends", resources=[],
                          estimated_time="45 min", gap_key="gap:g:1"),
        ],
        status=GapStatus.IDENTIFIED,
    )
