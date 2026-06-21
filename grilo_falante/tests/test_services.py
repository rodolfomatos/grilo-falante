"""Tests for services"""

import pytest
from grilo_falante.backend.services import (
    GFIDService,
    GMIFClassifier,
    FeynmanService,
    CognitiveLint,
    LintState,
)
from grilo_falante.models.enums import GMIFLevel
from grilo_falante.backend.services.feynman import FeynmanLevel


def test_gfid_generation():
    """Test GF-ID generation."""
    gfid = GFIDService.generate("test content", "M1")
    assert gfid.startswith("GF-")
    assert "-M1-" in gfid


def test_gfid_validation():
    """Test GF-ID validation."""
    valid_gfid = "GF-260415-M1-abc123"
    assert GFIDService.is_valid(valid_gfid) is True

    invalid_gfid = "invalid"
    assert GFIDService.is_valid(invalid_gfid) is False


def test_gmif_classification():
    """Test GMIF classification."""
    level, confidence = GMIFClassifier.classify(
        "The study shows that X causes Y",
        source_count=3,
    )
    assert level == GMIFLevel.VERIFIED


def test_cognitive_lint_blocking():
    """Test cognitive lint blocking patterns."""
    lint = CognitiveLint()

    # Should block
    result = lint.lint("This is obviously correct, just trust me.")
    assert result.state == LintState.REJECT

    # Should accept
    result = lint.lint("The data indicates a correlation.")
    assert result.state == LintState.ACCEPT


def test_feynman_explain():
    """Test Feynman explanation."""
    service = FeynmanService()
    result = service.explain("quantum entanglement", FeynmanLevel.CHILD)

    assert result.level == FeynmanLevel.CHILD
    assert len(result.concepts_identified) > 0


def test_graph_lint_orphans():
    """Test graph lint L1: orphan detection."""
    from grilo_falante.backend.services.graph_lint import GraphLinter
    from grilo_falante.models import GovernedClaim, GMIFLevel

    linter = GraphLinter()
    claims = [
        GovernedClaim(claim_key="c:1", claim_text="Referenced",
                      gmif_level=GMIFLevel.VERIFIED, gmif_confidence=0.9, claim_references=[]),
        GovernedClaim(claim_key="c:2", claim_text="References c:1",
                      gmif_level=GMIFLevel.DERIVED, gmif_confidence=0.7,
                      claim_references=["c:1"]),
        GovernedClaim(claim_key="c:orphan", claim_text="Alone",
                      gmif_level=GMIFLevel.UNVERIFIED, gmif_confidence=0.3, claim_references=[]),
    ]
    result = linter.run_all_checks(claims)
    issues = [i for i in result.issues if i.lint_code == "L1"]
    assert len(issues) == 1
    assert "c:orphan" in issues[0].claim_keys


def test_graph_lint_self_reference():
    """Test graph lint L2: self-referential detection."""
    from grilo_falante.backend.services.graph_lint import GraphLinter
    from grilo_falante.models import GovernedClaim, GMIFLevel

    linter = GraphLinter()
    claims = [
        GovernedClaim(claim_key="c:self", claim_text="Self ref",
                      gmif_level=GMIFLevel.INTERPRETATION, gmif_confidence=0.5,
                      claim_references=["c:self"]),
    ]
    result = linter.run_all_checks(claims)
    assert any(i.lint_code == "L2" for i in result.issues)


def test_graph_lint_get_references_claim_references():
    """Test _get_references prioritises claim_references over provenance."""
    from grilo_falante.backend.services.graph_lint import GraphLinter
    from grilo_falante.models import GovernedClaim, GMIFLevel

    linter = GraphLinter()
    claim = GovernedClaim(
        claim_key="c:test", claim_text="Test",
        gmif_level=GMIFLevel.VERIFIED, gmif_confidence=0.8,
        claim_references=["c:1", "c:2"],
        provenance={"references": ["c:old"]},
    )
    refs = linter._get_references(claim)
    assert refs == ["c:1", "c:2"]


def test_graph_lint_get_references_provenance_fallback():
    """Test _get_references falls back to provenance when claim_references is empty."""
    from grilo_falante.backend.services.graph_lint import GraphLinter
    from grilo_falante.models import GovernedClaim, GMIFLevel

    linter = GraphLinter()
    claim = GovernedClaim(
        claim_key="c:test", claim_text="Test",
        gmif_level=GMIFLevel.VERIFIED, gmif_confidence=0.8,
        claim_references=[],
        provenance={"references": ["c:old"]},
    )
    refs = linter._get_references(claim)
    assert refs == ["c:old"]


def test_learning_path_to_study_plan():
    """Test LearningPathGenerator.to_study_plan produces valid StudyPlan."""
    from grilo_falante.backend.services.learning_path import (
        LearningPathGenerator, LearningPath, LearningStep,
    )

    gen = LearningPathGenerator()
    path = LearningPath(
        topic="Test Topic",
        steps=[
            LearningStep(order=1, concept="Step 1", description="First step",
                         claim_keys=[], estimated_time="10m",
                         status="pending", is_gap=True, gap_key="gap:g:1"),
            LearningStep(order=2, concept="Step 2", description="Second step",
                         claim_keys=[], estimated_time="15m",
                         status="pending", is_gap=False),
        ],
        total_estimated_time="25m",
        prerequisites=[],
        gaps_found=1,
        claims_covered=0,
    )
    plan = gen.to_study_plan(path, "gap:g:1")
    assert plan.topic == "Test Topic"
    assert len(plan.steps) == 2
    assert plan.steps[0].gap_key == "gap:g:1"
    assert plan.steps[1].gap_key is None
    assert plan.status == "identified"


# ─── Graph Lint: L3-L8 ──────────────────────────────────────────────


def test_graph_lint_contradictions():
    """L3: Detect contradictory claims (same source, opposing positions)."""
    from grilo_falante.backend.services.graph_lint import GraphLinter
    from grilo_falante.models import GovernedClaim, GMIFLevel

    linter = GraphLinter()
    claims = [
        GovernedClaim(claim_key="c:pro", claim_text="X is true",
                      gmif_level=GMIFLevel.VERIFIED, gmif_confidence=0.9,
                      claim_references=[], source_id=1),
        GovernedClaim(claim_key="c:contra", claim_text="X is false",
                      gmif_level=GMIFLevel.CONFLICTED, gmif_confidence=0.1,
                      claim_references=[], source_id=1),
    ]
    result = linter.run_all_checks(claims)
    assert any(i.lint_code == "L3" for i in result.issues)


def test_graph_lint_cycles():
    """L4: Detect circular dependency chains."""
    from grilo_falante.backend.services.graph_lint import GraphLinter
    from grilo_falante.models import GovernedClaim, GMIFLevel

    linter = GraphLinter()
    claims = [
        GovernedClaim(claim_key="c:a", claim_text="A", gmif_level=GMIFLevel.DERIVED,
                      gmif_confidence=0.5, claim_references=["c:b"]),
        GovernedClaim(claim_key="c:b", claim_text="B", gmif_level=GMIFLevel.DERIVED,
                      gmif_confidence=0.5, claim_references=["c:c"]),
        GovernedClaim(claim_key="c:c", claim_text="C", gmif_level=GMIFLevel.DERIVED,
                      gmif_confidence=0.5, claim_references=["c:a"]),
    ]
    result = linter.run_all_checks(claims)
    assert any(i.lint_code == "L4" for i in result.issues)


def test_graph_lint_unsupported_conclusion():
    """L5: Detect conclusions only supported by CONFLICTED claims."""
    from grilo_falante.backend.services.graph_lint import GraphLinter
    from grilo_falante.models import GovernedClaim, GMIFLevel

    linter = GraphLinter()
    claims = [
        GovernedClaim(claim_key="c:doubt", claim_text="Doubtful source",
                      gmif_level=GMIFLevel.CONFLICTED, gmif_confidence=0.2,
                      claim_references=[]),
        GovernedClaim(claim_key="c:bad_conc", claim_text="Conclusion on bad data",
                      gmif_level=GMIFLevel.CONCLUSION, gmif_confidence=0.5,
                      claim_references=["c:doubt"]),
    ]
    result = linter.run_all_checks(claims)
    assert any(i.lint_code == "L5" for i in result.issues)


def test_graph_lint_missing_prerequisites():
    """L6: Detect CONCLUSION/SYNTHESIS without VERIFIED prerequisites."""
    from grilo_falante.backend.services.graph_lint import GraphLinter
    from grilo_falante.models import GovernedClaim, GMIFLevel

    linter = GraphLinter()
    claims = [
        GovernedClaim(claim_key="c:unverified", claim_text="Unverified",
                      gmif_level=GMIFLevel.UNVERIFIED, gmif_confidence=0.3,
                      claim_references=[]),
        GovernedClaim(claim_key="c:synth", claim_text="Synthesis on shaky ground",
                      gmif_level=GMIFLevel.SYNTHESIS, gmif_confidence=0.6,
                      claim_references=["c:unverified"]),
    ]
    result = linter.run_all_checks(claims)
    assert any(i.lint_code == "L6" for i in result.issues)


def test_graph_lint_no_false_positive_l6():
    """L6 should NOT fire when CONCLUSION has VERIFIED prerequisites."""
    from grilo_falante.backend.services.graph_lint import GraphLinter
    from grilo_falante.models import GovernedClaim, GMIFLevel

    linter = GraphLinter()
    claims = [
        GovernedClaim(claim_key="c:verified", claim_text="Verified fact",
                      gmif_level=GMIFLevel.VERIFIED, gmif_confidence=0.9,
                      claim_references=[]),
        GovernedClaim(claim_key="c:good_conc", claim_text="Valid conclusion",
                      gmif_level=GMIFLevel.CONCLUSION, gmif_confidence=0.8,
                      claim_references=["c:verified"]),
    ]
    result = linter.run_all_checks(claims)
    assert not any(i.lint_code == "L6" for i in result.issues)


def test_graph_lint_confidence_mismatch():
    """L7: Detect child confidence > parent confidence + 0.2."""
    from grilo_falante.backend.services.graph_lint import GraphLinter
    from grilo_falante.models import GovernedClaim, GMIFLevel

    linter = GraphLinter()
    claims = [
        GovernedClaim(claim_key="c:parent", claim_text="Parent claim",
                      gmif_level=GMIFLevel.VERIFIED, gmif_confidence=0.50,
                      claim_references=[]),
        GovernedClaim(claim_key="c:child", claim_text="Overconfident child",
                      gmif_level=GMIFLevel.DERIVED, gmif_confidence=0.99,
                      claim_references=["c:parent"]),
    ]
    result = linter.run_all_checks(claims)
    assert any(i.lint_code == "L7" for i in result.issues)


def test_graph_lint_temporal_inconsistency():
    """L8: Detect reference newer than claim (anachronism)."""
    from datetime import datetime, timedelta
    from grilo_falante.backend.services.graph_lint import GraphLinter
    from grilo_falante.models import GovernedClaim, GMIFLevel

    linter = GraphLinter()
    now = datetime.utcnow()
    claims = [
        GovernedClaim(claim_key="c:parent", claim_text="Parent claim",
                      gmif_level=GMIFLevel.VERIFIED, gmif_confidence=0.50,
                      claim_references=[]),
        GovernedClaim(claim_key="c:child", claim_text="Overconfident child",
                      gmif_level=GMIFLevel.DERIVED, gmif_confidence=0.99,
                      claim_references=["c:parent"]),
    ]

def test_graph_lint_temporal_inconsistency():
    """L8: Detect reference newer than claim (anachronism)."""
    from datetime import datetime, timedelta
    from grilo_falante.backend.services.graph_lint import GraphLinter
    from grilo_falante.models import GovernedClaim, GMIFLevel

    linter = GraphLinter()
    now = datetime.utcnow()
    claims = [
        GovernedClaim(claim_key="c:old", claim_text="Old claim",
                      gmif_level=GMIFLevel.VERIFIED, gmif_confidence=0.9,
                      claim_references=[],
                      created_at=now - timedelta(days=10)),
        GovernedClaim(claim_key="c:anachron", claim_text="Anachronistic",
                      gmif_level=GMIFLevel.SYNTHESIS, gmif_confidence=0.6,
                      claim_references=["c:old"],
                      created_at=now - timedelta(days=20)),
    ]
    result = linter.run_all_checks(claims)
    assert any(i.lint_code == "L8" for i in result.issues)


# ─── Graph Lint: Multilint (sample claims) ──────────────────────────


def test_graph_lint_multilint(sample_claims):
    """Run L1-L8 on the full sample_claims fixture. Documents pass/fail per check."""
    from grilo_falante.backend.services.graph_lint import GraphLinter

    linter = GraphLinter()
    result = linter.run_all_checks(sample_claims)

    codes_found = {i.lint_code for i in result.issues}
    print(f"\nEpistemic Lint Results on sample_claims ({len(sample_claims)} claims):")
    print(f"  Passed: {result.passed}")
    for code in sorted(codes_found):
        count = sum(1 for i in result.issues if i.lint_code == code)
        print(f"  {code}: {count} issue(s)")
    print(f"  Summary: {result.summary}")

    assert len(result.issues) > 0  # sample claims should trigger some lint


# ─── Source Registry ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_source_registry_defaults():
    """TrustedSourceRegistry initializes with Tier 1 default sources."""
    from grilo_falante.backend.services.source_registry import TrustedSourceRegistry

    registry = TrustedSourceRegistry()
    tier1 = registry.list_tier1()
    assert len(tier1) >= 5  # arxiv, pubmed, ieee, acm, openalex
    assert registry.is_trusted("arxiv")
    assert not registry.is_trusted("unknown_source")


@pytest.mark.asyncio
async def test_source_registry_can_add_tier1():
    """can_add_tier1 validates curator score threshold."""
    from grilo_falante.backend.services.source_registry import TrustedSourceRegistry

    registry = TrustedSourceRegistry()
    assert registry.can_add_tier1(curator_score=0.9) is True
    assert registry.can_add_tier1(curator_score=0.5) is False


@pytest.mark.asyncio
async def test_source_registry_propose_addition():
    """Proposing a Tier 1 source requires curator_score > 0.7."""
    from grilo_falante.backend.services.source_registry import (
        TrustedSourceRegistry,
        CurationStatus,
    )
    from grilo_falante.models import SourceTier

    registry = TrustedSourceRegistry()
    with pytest.raises(ValueError, match="score"):
        await registry.propose_addition(
            source_key="test_journal",
            name="Test Journal",
            url="https://test-journal.org",
            domains=["testing"],
            tier=SourceTier.TIER_1,
            proposer_curator_id=1,
            curator_score=0.5,
        )
    # With sufficient score it should succeed
    proposal = await registry.propose_addition(
        source_key="test_journal",
        name="Test Journal",
        url="https://test-journal.org",
        domains=["testing"],
        tier=SourceTier.TIER_2,
        proposer_curator_id=1,
        curator_score=0.5,
    )
    assert proposal.status == CurationStatus.PENDING
    assert proposal.source_key == "test_journal"


# ─── Learning Path Generator ────────────────────────────────────────


@pytest.mark.asyncio
async def test_learning_path_generate_path(sample_claims, sample_gaps):
    """LearningPathGenerator.generate produces ordered steps from claims+gaps."""
    from grilo_falante.backend.services.learning_path import LearningPathGenerator

    gen = LearningPathGenerator()
    path = await gen.generate(
        topic="Climate Change Analysis",
        existing_claims=sample_claims,
        identified_gaps=sample_gaps,
    )
    assert path.topic == "Climate Change Analysis"
    assert len(path.steps) > 0
    assert path.total_estimated_time != ""
    for i, step in enumerate(path.steps):
        assert step.order == i + 1


@pytest.mark.asyncio
async def test_learning_path_to_markdown(sample_claims, sample_gaps):
    """LearningPathGenerator.to_markdown produces valid markdown."""
    from grilo_falante.backend.services.learning_path import LearningPathGenerator

    gen = LearningPathGenerator()
    path = await gen.generate(topic="Test", existing_claims=sample_claims,
                              identified_gaps=sample_gaps)
    md = gen.to_markdown(path)
    assert path.topic in md
    assert md.startswith("#")
    assert "## Steps" in md


# ─── Active Search ──────────────────────────────────────────────────


def test_active_search_imports():
    """ActiveSearchService imports without error."""
    from grilo_falante.backend.services.active_search import ActiveSearchService
    assert ActiveSearchService is not None


def test_curator_service_imports():
    """Curator service imports without error."""
    from grilo_falante.backend.services.curator import CuratorScoringService
    assert CuratorScoringService is not None
