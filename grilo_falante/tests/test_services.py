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
    assert level == GMIFLevel.M1_PRIMARY


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
