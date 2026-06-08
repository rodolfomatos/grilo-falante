"""
Feynman Service — Feynman Explanation Protocol (FEP)

Implements three levels of explanation:
- FEP-1: Child level (3rd grade, no jargon)
- FEP-2: Expert level (precise definitions, assumptions)
- FEP-3: "Why" cycle (until axiom or gap)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class FeynmanLevel(str, Enum):
    """Feynman explanation levels."""

    CHILD = "fep1"  # 3rd grade, no jargon
    EXPERT = "fep2"  # Precise definitions
    WHY = "fep3"  # "Why" until axiom


@dataclass
class FeynmanExplanation:
    """Result of Feynman explanation."""

    level: FeynmanLevel
    explanation: str
    concepts_identified: list[str]
    gaps_found: list[str]
    completed: bool
    axiom_reached: Optional[str] = None


class FeynmanService:
    """
    Service for generating Feynman-style explanations.

    FEP-1: Child level - Simple analogies, no jargon
    FEP-2: Expert level - Precise, with assumptions
    FEP-3: "Why" cycle - Until axiom or gap
    """

    STOP_WORDS = {"the", "a", "an", "is", "are", "was", "were", "be", "been"}

    def explain(
        self,
        topic: str,
        level: FeynmanLevel = FeynmanLevel.CHILD,
        context: Optional[dict] = None,
    ) -> FeynmanExplanation:
        """
        Generate explanation at specified level.

        Args:
            topic: Topic to explain
            level: FEP level (child, expert, why)
            context: Additional context

        Returns:
            FeynmanExplanation with explanation and metadata
        """
        if level == FeynmanLevel.CHILD:
            return self._explain_child(topic, context)
        elif level == FeynmanLevel.EXPERT:
            return self._explain_expert(topic, context)
        elif level == FeynmanLevel.WHY:
            return self._explain_why(topic, context)
        else:
            raise ValueError(f"Unknown level: {level}")

    def _explain_child(self, topic: str, context: Optional[dict]) -> FeynmanExplanation:
        """Generate child-level explanation (FEP-1)."""
        concepts = self._extract_concepts(topic)

        explanation_parts = []
        gaps = []

        # Simple analogies and core concepts
        for concept in concepts[:3]:
            explanation_parts.append(f"Think of {concept} like a [analogy needed - this is a gap]")
            gaps.append(f"Analogy for: {concept}")

        explanation = f"""
## {topic} — Simple Explanation

{self._join_explanations(explanation_parts)}

**Remember:** This is the simple version. If something doesn't make sense,
ask "why" and we'll go deeper!
"""
        return FeynmanExplanation(
            level=FeynmanLevel.CHILD,
            explanation=explanation.strip(),
            concepts_identified=concepts,
            gaps_found=gaps,
            completed=True,
        )

    def _explain_expert(self, topic: str, context: Optional[dict]) -> FeynmanExplanation:
        """Generate expert-level explanation (FEP-2)."""
        concepts = self._extract_concepts(topic)

        explanation_parts = []

        for concept in concepts[:5]:
            explanation_parts.append(
                f"**{concept}**: [Precise definition needed] "
                f"- Assumptions: [list], Limitations: [list]"
            )

        explanation = f"""
## {topic} — Expert Level

### Definitions
{chr(10).join(explanation_parts)}

### Assumptions
- [Explicit assumption 1]
- [Explicit assumption 2]

### Limitations
- [Known limitation 1]
- [Known limitation 2]

### Evidence
- [Evidence strength assessment]
"""

        return FeynmanExplanation(
            level=FeynmanLevel.EXPERT,
            explanation=explanation.strip(),
            concepts_identified=concepts,
            gaps_found=["Definitions need verification"],
            completed=False,
        )

    def _explain_why(self, topic: str, context: Optional[dict]) -> FeynmanExplanation:
        """
        Generate "why" cycle explanation (FEP-3).

        Keeps asking "why" until reaching:
        1. An axiom (self-evident truth)
        2. A primitive (undefined term)
        3. A gap (can't answer)
        4. Contradiction (invalidates)
        """
        why_chain = []
        gaps = []
        current_topic = topic
        max_depth = 5

        for depth in range(max_depth):
            why_chain.append(current_topic)
            next_topic = self._ask_why(current_topic, depth)

            if next_topic is None:
                gaps.append(f"Cannot answer 'why' for: {current_topic}")
                break

            if self._is_axiom(next_topic):
                return FeynmanExplanation(
                    level=FeynmanLevel.WHY,
                    explanation=self._format_why_chain(why_chain, next_topic),
                    concepts_identified=why_chain,
                    gaps_found=gaps,
                    completed=True,
                    axiom_reached=next_topic,
                )

            current_topic = next_topic

        return FeynmanExplanation(
            level=FeynmanLevel.WHY,
            explanation=self._format_why_chain(why_chain, None),
            concepts_identified=why_chain,
            gaps_found=gaps + ["Max depth reached"],
            completed=False,
        )

    def _ask_why(self, statement: str, depth: int) -> Optional[str]:
        """Ask 'why' about a statement. Returns next level or None if at axiom."""
        concepts = self._extract_concepts(statement)
        if not concepts:
            return None

        # Simplified: move to next concept
        if depth < len(concepts) - 1:
            return concepts[depth + 1]
        return None

    def _is_axiom(self, statement: str) -> bool:
        """Check if statement is an axiom (self-evident or primitive)."""
        axioms = {
            "existence",
            "consciousness",
            "mathematical truth",
            "logical primitive",
        }
        statement_lower = statement.lower()
        return any(ax in statement_lower for ax in axioms)

    def _extract_concepts(self, text: str) -> list[str]:
        """Extract key concepts from text."""
        import re

        words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())
        concepts = [w for w in words if w not in self.STOP_WORDS]
        return list(dict.fromkeys(concepts))[:5]

    def _join_explanations(self, parts: list[str]) -> str:
        """Join explanation parts."""
        return "\n\n".join(f"- {part}" for part in parts)

    def _format_why_chain(self, chain: list[str], final: Optional[str]) -> str:
        """Format the why chain for display."""
        lines = []
        for i, item in enumerate(chain):
            indent = "  " * i
            lines.append(f"{indent}{i+1}. {item}")

        if final:
            lines.append(f"\n→ Axiom reached: {final}")

        return "\n".join(lines)

    def double_feynman(self, source_text: str) -> tuple[list[str], list[str]]:
        """
        Double Feynman validation.

        F1: Extract explicit claims (what author says)
        F2: Identify projections (what author doesn't say but readers infer)

        Args:
            source_text: Source document text

        Returns:
            Tuple of (f1_claims, f2_projections)
        """
        # Simplified implementation
        f1_claims = []
        f2_projections = []

        # In real implementation, this would use LLM
        sentences = source_text.split(".")

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:
                continue

            # Simple heuristics
            if any(kw in sentence.lower() for kw in ["shows", "demonstrates", "measured", "data"]):
                f1_claims.append(sentence)

            if any(
                kw in sentence.lower()
                for kw in ["therefore", "thus", "consequently", "all", "always"]
            ):
                f2_projections.append(f"[POTENTIAL PROJECTION] {sentence}")

        return f1_claims, f2_projections
