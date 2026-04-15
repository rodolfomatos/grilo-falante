"""
Claims Extractor - Extract claims from content

Extracts individual claims from text, chat, or structured content.
"""

import re
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Claim:
    """An extracted claim."""
    id: str
    text: str
    type: str  # fact, opinion, hypothesis, question
    anchors: List[str]  # source references
    dependencies: List[str]  # depends on other claims
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "text": self.text,
            "type": self.type,
            "anchors": self.anchors,
            "dependencies": self.dependencies,
        }


class ClaimsExtractor:
    """
    Extracts claims from various content types.
    
    Supports:
    - Plain text (paragraphs → claims)
    - Chat messages (individual messages → claims)
    - Structured content (JSON/YAML → claims)
    - Scientific articles (abstract, methods, results → claims)
    """
    
    # Claim indicators
    INDICATORS_FACT = [
        "é", "são", "existe", "existem", "tem", "têm",
        "was", "is", "are", "has", "have", "exists",
    ]
    INDICATORS_OPINION = [
        "acho que", "penso que", "acredito que",
        "I think", "I believe", "I assume",
    ]
    INDICATORS_HYPOTHESIS = [
        "pode ser", "poderá", "será possível",
        "may be", "could be", "might be",
    ]
    INDICATORS_QUESTION = [
        "?", "como?", "porque?", "porquê?",
        "what", "why", "how", "when", "where",
    ]
    
    def __init__(self):
        self.claim_counter = 0
    
    def _generate_id(self) -> str:
        """Generate unique claim ID."""
        self.claim_counter += 1
        timestamp = datetime.now().strftime("%y%m%d")
        return f"CL{timestamp}-{self.claim_counter:04d}"
    
    def extract_from_text(
        self,
        text: str,
        source_id: Optional[str] = None,
    ) -> List[Claim]:
        """
        Extract claims from plain text.
        
        Splits by sentences and classifies each.
        """
        claims = []
        source = source_id or "text"
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        for sentence in sentences:
            claim_type = self._classify_sentence(sentence)
            
            claim = Claim(
                id=self._generate_id(),
                text=sentence,
                type=claim_type,
                anchors=[source],
                dependencies=[],
            )
            claims.append(claim)
        
        logger.info(f"Extracted {len(claims)} claims from text")
        return claims
    
    def extract_from_chat(
        self,
        messages: List[Dict],
        session_id: str,
    ) -> List[Claim]:
        """
        Extract claims from chat messages.
        
        Messages format: [{"role": "user"|"assistant", "content": "...", ...}]
        """
        claims = []
        message_claims = set()
        
        for i, msg in enumerate(messages):
            content = msg.get("content", "")
            role = msg.get("role", "assistant")
            
            # Extract sentences from each message
            sentences = re.split(r'[.!?]+', content)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            for sentence in sentences:
                # Skip very short or question-only
                if len(sentence) < 20 or sentence.endswith("?"):
                    continue
                
                claim_type = self._classify_sentence(sentence)
                
                claim = Claim(
                    id=self._generate_id(),
                    text=sentence,
                    type=claim_type,
                    anchors=[f"{session_id}:{role}"],
                    dependencies=list(message_claims),
                )
                claims.append(claim)
                
                # Track significant claims for dependency
                if claim_type == "fact":
                    message_claims.add(claim.id)
        
        logger.info(f"Extracted {len(claims)} claims from {len(messages)} messages")
        return claims
    
    def extract_from_article(
        self,
        article: Dict,
        doi: Optional[str] = None,
    ) -> List[Claim]:
        """
        Extract claims from scientific article.
        
        Expected structure:
        {
            "title": "...",
            "abstract": "...",
            "sections": [{"title": "...", "content": "..."}]
        }
        """
        claims = []
        
        # Title claim
        title = article.get("title", "")
        if title:
            claims.append(Claim(
                id=self._generate_id(),
                text=f"Artigo: {title}",
                type="fact",
                anchors=[doi or "unknown"],
                dependencies=[],
            ))
        
        # Abstract claims
        abstract = article.get("abstract", "")
        if abstract:
            abstract_claims = self.extract_from_text(abstract, doi)
            claims.extend(abstract_claims)
        
        # Section claims
        for section in article.get("sections", []):
            section_title = section.get("title", "")
            section_content = section.get("content", "")
            
            if section_content:
                section_claims = self.extract_from_text(
                    section_content,
                    f"{doi}:{section_title}" if doi else section_title
                )
                claims.extend(section_claims)
        
        logger.info(f"Extracted {len(claims)} claims from article")
        return claims
    
    def extract_from_decision(
        self,
        decision: Dict,
    ) -> List[Claim]:
        """Extract claims from a structured decision."""
        claims = []
        
        # Main decision claim
        decision_text = decision.get("decision", "")
        if decision_text:
            claims.append(Claim(
                id=self._generate_id(),
                text=decision_text,
                type="fact",
                anchors=[decision.get("id", "decision")],
                dependencies=[],
            ))
        
        # Rationale claims
        for rationale in decision.get("rationale", []):
            claims.append(Claim(
                id=self._generate_id(),
                text=rationale.get("text", ""),
                type="opinion",
                anchors=[rationale.get("source", "")],
                dependencies=[],
            ))
        
        # Source claims
        for source in decision.get("sources", []):
            claims.append(Claim(
                id=self._generate_id(),
                text=f"Fonte: {source.get('reference', '')}",
                type="fact",
                anchors=[source.get("id", "")],
                dependencies=[],
            ))
        
        return claims
    
    def _classify_sentence(self, sentence: str) -> str:
        """Classify a sentence type."""
        sentence_lower = sentence.lower()
        
        # Question
        if sentence.endswith("?") or any(
            q in sentence_lower for q in ["como?", "porque?", "porquê?", "what", "why", "how"]
        ):
            return "question"
        
        # Hypothesis
        if any(h in sentence_lower for h in self.INDICATORS_HYPOTHESIS):
            return "hypothesis"
        
        # Opinion
        if any(o in sentence_lower for o in self.INDICATORS_OPINION):
            return "opinion"
        
        # Fact
        if any(f in sentence_lower for f in self.INDICATORS_FACT):
            return "fact"
        
        return "opinion"


# Singleton
_extractor: Optional[ClaimsExtractor] = None


def get_claims_extractor() -> ClaimsExtractor:
    global _extractor
    if _extractor is None:
        _extractor = ClaimsExtractor()
    return _extractor