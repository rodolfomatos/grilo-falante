"""
Feynman Processor Service.

Processes content through 3 Feynman levels:
- F1: Simple explanation for a child (criança)
- F2: Technical explanation for experts (especialista)
- F3: Why Loop - gap detection ("Porquê? Porque X. Porque Y...")

This service wraps the existing app/services/feynman_synthesize.py and
app/services/why_loop.py into a unified interface.
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from grilo_falante.platform.config import get_llm_config

logger = logging.getLogger(__name__)


@dataclass
class FeynmanF1:
    """F1 - Explanation for a child (criança)."""
    content: str
    simplified_terms: Dict[str, str] = field(default_factory=dict)
    word_count: int = 0
    analogias: List[str] = field(default_factory=list)


@dataclass
class FeynmanF2:
    """F2 - Technical explanation for experts (especialista)."""
    content: str
    sources: List[str] = field(default_factory=list)
    technical_terms: List[str] = field(default_factory=list)
    word_count: int = 0


@dataclass
class FeynmanF3:
    """F3 - Why Loop for gap detection."""
    questions: List[Dict[str, Any]] = field(default_factory=list)
    gaps_detected: List[str] = field(default_factory=list)
    depth_reached: int = 0
    status: str = "pending"


@dataclass
class FeynmanResult:
    """Complete result from Feynman processing."""
    f1: FeynmanF1
    f2: FeynmanF2
    f3: FeynmanF3
    source_content: str
    topic: str
    processing_successful: bool = True
    error: Optional[str] = None


class FeynmanProcessor:
    """
    Unified Feynman processor for F1/F2/F3 levels.

    Usage:
        processor = FeynmanProcessor()
        result = processor.process(content="Alan Turing foi um matemático...", topic="Alan Turing")
        print(result.f1.content)  # Simple explanation
        print(result.f2.content)  # Technical explanation
        print(result.f3.gaps_detected)  # Identified gaps
    """

    SIMPLE_TERMS = {
        "consciência": "consciência é como uma lanterna que ilumina os nossos pensamentos",
        "IA": "computador que pensa como um humano",
        "memória": "uma gaveta na mente onde guardamos coisas",
        "aprendizagem": "aprender é como crescer - vamos知道了 mais coisas",
        "algoritmo": "uma receita de bolo - passos para fazer algo",
        "neurónio": "uma pequena célula no cérebro que ajuda a pensar",
        "sinapse": "uma ponte entre células do cérebro",
        "processador": "o cérebro do computador",
        "base de dados": "uma biblioteca organizada de informações",
        "servidor": "um computador especial que ajuda outros computadores",
    }

    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    def process(
        self,
        content: str,
        topic: str,
        include_f1: bool = True,
        include_f2: bool = True,
        include_f3: bool = True,
    ) -> FeynmanResult:
        """
        Process content through Feynman F1/F2/F3 levels.

        Args:
            content: The content to process
            topic: The main topic/subject
            include_f1: Whether to generate F1 (child explanation)
            include_f2: Whether to generate F2 (expert explanation)
            include_f3: Whether to generate F3 (why loop)

        Returns:
            FeynmanResult with all 3 levels
        """
        try:
            f1_result = self._process_f1(content) if include_f1 else FeynmanF1(content="", word_count=0)
            f2_result = self._process_f2(content) if include_f2 else FeynmanF2(content="", word_count=0)
            f3_result = self._process_f3(f2_result.content if include_f2 else content, topic) if include_f3 else FeynmanF3()

            return FeynmanResult(
                f1=f1_result,
                f2=f2_result,
                f3=f3_result,
                source_content=content,
                topic=topic,
                processing_successful=True,
            )

        except Exception as e:
            logger.error(f"Feynman processing error: {e}")
            return FeynmanResult(
                f1=FeynmanF1(content="", word_count=0),
                f2=FeynmanF2(content="", word_count=0),
                f3=FeynmanF3(),
                source_content=content,
                topic=topic,
                processing_successful=False,
                error=str(e),
            )

    def _process_f1(self, content: str) -> FeynmanF1:
        """Generate F1 - Simple explanation for a child."""
        text = content.strip()

        simplified_terms = {}
        analogias = []

        for term, simple_def in self.SIMPLE_TERMS.items():
            pattern = rf'\b{term}s?\b'
            if re.search(pattern, text, re.IGNORECASE):
                simplified_terms[term] = simple_def
                text = re.sub(pattern, simple_def.split(" ")[0], text, flags=re.IGNORECASE)
                analogias.append(f"{term} → {simple_def}")

        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s,.\-áéíóúàèìòùãẽĩõũç?!]', '', text)

        sentences = text.split(".")
        simple_sentences = []
        for sent in sentences[:5]:
            sent = sent.strip()
            if len(sent) > 10:
                simple_sentences.append(sent)

        final_text = ". ".join(simple_sentences)
        if final_text and not final_text.endswith("."):
            final_text += "."

        return FeynmanF1(
            content=final_text,
            simplified_terms=simplified_terms,
            word_count=len(final_text.split()),
            analogias=analogias,
        )

    def _process_f2(self, content: str) -> FeynmanF2:
        """Generate F2 - Technical explanation for experts."""
        text = content.strip()

        technical_terms = self._extract_technical_terms(text)

        sources = self._extract_sources(text)

        text = re.sub(r'\s+', ' ', text)

        sentences = text.split(".")
        tech_sentences = []
        for sent in sentences:
            sent = sent.strip()
            if len(sent) > 20:
                tech_sentences.append(sent)

        final_text = ". ".join(tech_sentences[:10])
        if final_text and not final_text.endswith("."):
            final_text += "."

        return FeynmanF2(
            content=final_text,
            sources=sources,
            technical_terms=technical_terms,
            word_count=len(final_text.split()),
        )

    def _process_f3(self, content: str, topic: str) -> FeynmanF3:
        """Generate F3 - Why Loop for gap detection."""
        questions = []
        gaps_detected = []

        claims = re.findall(
            r'([^.]+(?:é|foi|foi|cria|descobre|define|estabelece|propõe)[^.]+\.)',
            content
        )

        if not claims:
            gaps_detected.append(f"O que é {topic} exactamente?")
            gaps_detected.append(f"Porque é que {topic} é importante?")
            questions.append({
                "question": f"Porque é que {topic}?",
                "depth": 1,
                "status": "pending",
                "type": "root_why"
            })
            return FeynmanF3(
                questions=questions,
                gaps_detected=gaps_detected,
                depth_reached=1,
                status="partial",
            )

        why_templates = [
            (1, "Mas porquê? {claim}"),
            (2, "E como sabemos que isso é verdade?"),
            (3, "Existe alguma excepção?"),
        ]

        for i, claim in enumerate(claims[:3]):
            claim_short = claim[:60] + "..." if len(claim) > 60 else claim

            for depth, template in why_templates[:1]:
                question = template.format(claim=claim_short)
                questions.append({
                    "question": question,
                    "depth": depth,
                    "status": "pending",
                    "type": "why_loop",
                    "source_claim": claim[:100],
                })
                gaps_detected.append(f"Porque é que: {claim_short}")

        depth = len(set(q["depth"] for q in questions))

        return FeynmanF3(
            questions=questions,
            gaps_detected=gaps_detected[:5],
            depth_reached=depth,
            status="complete" if questions else "no_claims",
        )

    def _extract_technical_terms(self, text: str) -> List[str]:
        """Extract technical terms from content."""
        technical_patterns = [
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:teoria|modelo|método|sistema)\b',
            r'\b(?:algoritmo|protocolo|arquitectura|implementação)\b',
            r'\b(?:\d+(?:\.\d+)?(?:\s*[%°±])?)\b',
        ]

        terms = []
        for pattern in technical_patterns:
            matches = re.findall(pattern, text)
            terms.extend(matches)

        return list(set(terms))[:10]

    def _extract_sources(self, text: str) -> List[str]:
        """Extract potential sources from content."""
        source_patterns = [
            r'(?:segundo|conforme|de acordo com)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'(?:citado|referenciado)\s+por\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        ]

        sources = []
        for pattern in source_patterns:
            matches = re.findall(pattern, text)
            sources.extend(matches)

        return list(set(sources))[:5]

    def generate_faq_from_f1(
        self,
        f1_result: FeynmanF1,
        topic: str,
    ) -> List[Dict[str, str]]:
        """
        Generate FAQ Q&A pairs from F1 explanation.

        Returns list of {question, answer} dicts.
        """
        faqs = []

        faqs.append({
            "question": f"O que é {topic}?",
            "answer": f1_result.content,
        })

        for analogia in f1_result.analogias[:2]:
            parts = analogia.split(" → ")
            if len(parts) == 2:
                term, explanation = parts
                faqs.append({
                    "question": f" O que é {term}?",
                    "answer": explanation,
                })

        return faqs

    def format_result_summary(self, result: FeynmanResult) -> str:
        """Format a human-readable summary of Feynman processing."""
        lines = [
            f"=== Feynman Processing: {result.topic} ===",
            "",
            f"[F1 - Para Crianças]",
            f"{result.f1.content}",
            f"(~{result.f1.word_count} palavras)",
            "",
            f"[F2 - Para Especialistas]",
            f"{result.f2.content}",
            f"(~{result.f2.word_count} palavras)",
            "",
            f"[F3 - Why Loop]",
            f"Gaps detectados: {len(result.f3.gaps_detected)}",
        ]

        for gap in result.f3.gaps_detected[:3]:
            lines.append(f"  - {gap}")

        return "\n".join(lines)
