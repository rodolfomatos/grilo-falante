"""
Why Loop Service - Recursive "porquê?" questioning

From prototype: generates depth-based why questions to deepen understanding.

Strategy:
- For each claim, ask "but why?"
- Up to 3 iterations
- Or until no more legitimate questions
"""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class WhyQuestion:
    question: str
    depth: int
    status: str


@dataclass
class WhyLoopResult:
    questions: list[dict]
    final_depth: int
    status: str


class WhyLoopService:
    """
    Loop de perguntas "porquê?".

    Templates by depth:
    - Depth 1: "Mas porquê?", "Porque é que {topic}?"
    - Depth 2: "E como sabemos que isso é verdade?", "Qual é a evidência?"
    - Depth 3: "E se a exceção for verdade?", "Há alguma teoria rival?"
    """

    QUESTION_TEMPLATES = {
        1: [
            "Mas porquê?",
            "Porque é que isso acontece?",
            "O que faz {topic} ser assim?",
        ],
        2: [
            "E como sabemos que isso é verdade?",
            "Qual é a evidência para isso?",
            "Existe exceção a isto?",
        ],
        3: [
            "E se a exceção for verdade?",
            "Há alguma teoria rival?",
            "O que acontece quando não se cumpre?",
        ],
    }

    def __init__(self, max_depth: int = 3):
        self.max_depth = max_depth

    def extract_claims(self, text: str) -> list[str]:
        """Extract key claims from text."""
        patterns = [
            r"([^.]+(?:é|foi|foi|cria|descobre|mostra|prov[ao])[^.]+\.)",
            r"([^.]*[A-Z][^.]+\.)",
        ]

        claims = []
        for pattern in patterns:
            found = re.findall(pattern, text)
            claims.extend(found)

        return claims[:5]

    def generate_questions(
        self,
        synthesis_content: str,
        topic: str,
        current_depth: int = 1
    ) -> list[WhyQuestion]:
        """Generate why questions for a synthesis."""
        if current_depth > self.max_depth:
            return []

        questions = []
        claims = self.extract_claims(synthesis_content)

        if not claims:
            questions.append(WhyQuestion(
                question=f"Mas porquê? O que acontece se não for verdade?",
                depth=current_depth,
                status="pending"
            ))
            return questions

        templates = self.QUESTION_TEMPLATES.get(current_depth, self.QUESTION_TEMPLATES[1])

        for i, claim in enumerate(claims[:3]):
            template = templates[i % len(templates)]
            question_text = template.replace("{topic}", topic[:30])

            questions.append(WhyQuestion(
                question=question_text,
                depth=current_depth,
                status="pending"
            ))

        return questions

    def execute(
        self,
        synthesis_expert: str,
        topic: str,
        max_iterations: int = 3
    ) -> WhyLoopResult:
        """
        Run the full "porquê?" loop.

        Args:
            synthesis_expert: Expert-level synthesis text
            topic: The topic being discussed
            max_iterations: Maximum iterations (capped at self.max_depth)

        Returns:
            WhyLoopResult with questions and depth reached
        """
        all_questions = []
        iteration = 0
        current_content = synthesis_expert

        while iteration < min(max_iterations, self.max_depth):
            questions = self.generate_questions(
                current_content,
                topic,
                iteration + 1
            )

            if not questions:
                break

            all_questions.extend(questions)
            iteration += 1

        return WhyLoopResult(
            questions=[{"q": q.question, "depth": q.depth, "status": q.status} for q in all_questions],
            final_depth=iteration,
            status="complete" if all_questions else "no_questions"
        )

    def format_output(self, result: WhyLoopResult) -> str:
        """Format output for display."""
        if not result.questions:
            return "Nenhuma pergunta gerada."

        lines = ["**Perguntas de Profundidade:**"]

        for item in result.questions:
            depth = item["depth"]
            q = item["q"]
            lines.append(f"\n{depth}. {q}")

        return "\n".join(lines)