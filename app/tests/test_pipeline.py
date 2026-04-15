"""
Tests for Grilo Falante Skill
"""

import pytest
from app.services.pipeline import Pipeline
from app.data.memory.graph.gmif import GMIFClassifier


class TestGMIF:
    """Test GMIF classifier."""
    
    def test_classify_primary_evidence(self):
        """M1 requires multiple sources, high confidence."""
        classifier = GMIFClassifier()
        
        result = classifier.classify(
            claim="Portugal é um país da UE",
            confidence=0.9,
            sources=[
                {"id": "fonte1", "type": "legal"},
                {"id": "fonte2", "type": "legal"},
            ],
            risks=[],
            assumptions=[],
        )
        
        assert result.type.value == "M1"
    
    def test_classify_with_assumptions(self):
        """M2 when there are assumptions."""
        classifier = GMIFClassifier()
        
        result = classifier.classify(
            claim="Pode ser dedutível",
            confidence=0.6,
            sources=[{"id": "fonte1", "type": "legal"}],
            risks=[],
            assumptions=["assumpt1"],
        )
        
        assert result.type.value == "M2"
    
    def test_classify_doubtful(self):
        """M4 when contradictions detected."""
        classifier = GMIFClassifier()
        
        result = classifier.classify(
            claim="É dedutível",
            confidence=0.8,
            sources=[{"id": "fonte1", "type": "legal"}],
            risks=[],
            assumptions=[],
            contradictions=[{"description": "Contradiction found"}],
        )
        
        assert result.type.value == "M4"
    
    def test_classify_partial(self):
        """M3 default classification."""
        classifier = GMIFClassifier()
        
        result = classifier.classify(
            claim="Talvez seja possível",
            confidence=0.3,
            sources=[],
            risks=[],
            assumptions=[],
        )
        
        assert result.type.value == "M3"


class TestPipeline:
    """Test analysis pipeline."""
    
    @pytest.mark.asyncio
    async def test_analyse_text(self):
        """Test plain text analysis."""
        pipeline = Pipeline()
        
        result = await pipeline.analyse(
            content="A educação em Portugal tem três níveis: básico, secundário e superior.",
            content_type="text",
            metadata={"confidence": 0.7},
        )
        
        assert len(result.claims) > 0
        assert len(result.gf_ids) > 0
    
    @pytest.mark.asyncio
    async def test_analyse_chat(self):
        """Test chat analysis."""
        pipeline = Pipeline()
        
        messages = [
            {"role": "user", "content": "O que é o Grilo Falante?"},
            {"role": "assistant", "content": "É um regime de governação cognitiva."},
        ]
        
        result = await pipeline.analyse(
            content=messages,
            content_type="chat",
            metadata={"session_id": "test_session"},
        )
        
        assert len(result.claims) > 0
    
    @pytest.mark.asyncio
    async def test_analyse_decision(self):
        """Test decision analysis."""
        pipeline = Pipeline()
        
        decision = {
            "id": "dec001",
            "decision": "Despesa dedutível",
            "rationale": [{"text": "Cumpre requisitos"}],
            "sources": [{"id": "civa23", "reference": "Artigo 23º CIVA"}],
        }
        
        result = await pipeline.analyse(
            content=decision,
            content_type="decision",
            metadata={"confidence": 0.8},
        )
        
        assert len(result.claims) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])