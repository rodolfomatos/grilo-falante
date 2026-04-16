"""
Falacia Detection Service.

Detects logical fallacies between claims and propagates
recursively to all affected islands.

Types of fallacies detected:
- CONTRADICTION: Two claims contradict each other
- GENERALIZATION: Overly broad claim without qualification
- APPEAL_TO_AUTHORITY: Claim based on authority without verification
- APPEAL_TO_MAJORITY: "Everyone says so" without evidence
- CAUSAL_FALLACY: Assuming causation from correlation
- STRAWMAN: Misrepresenting an argument
- FALSE_DILEMMA: Presenting only two options when more exist
- CIRCULAR_REASONING: Claim uses itself as evidence
"""

import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple

from grilo_admin.models.article import (
    Falacia,
    FalaciaCreate,
    FalaciaType,
    FalaciaSeverity,
    FalaciaStatus,
    ArticleClaim,
    GMIFLevel,
)

logger = logging.getLogger(__name__)


class FalaciaDetector:
    """
    Detects logical fallacies in claims.

    Uses pattern matching and heuristics to identify
    common logical fallacies.
    """

    PATTERNS = {
        FalaciaType.CONTRADICTION: [
            (r'\bno entanto\b', r'\bmas\b'),
            (r'\bpor outro lado\b', r'\bcontradiz\b'),
            (r'\bé falso que\b', r'\bé verdade que\b'),
            (r'\bnunca\b.*\b sempre\b', None),
            (r'\btodos\b.*\bnenhum\b', None),
        ],
        FalaciaType.GENERALIZATION: [
            (r'\btodos os\b', None),
            (r'\btodas as\b', None),
            (r'\bsempre\b', None),
            (r'\nunca\b', None),
            (r'\bdeixa-me dizer\b.*\é sempre\b', None),
        ],
        FalaciaType.APPEAL_TO_AUTHORITY: [
            (r'\b(cientistas|especialistas|expertos)\b.*\b(dizem|afirmam|confirmam)\b', None),
            (r'\bsegundo\b.*\b(dizem|afirmam)\b', None),
            (r'\bcomo\b.*\b(diz|dizia)\b.*\bé\b', None),
        ],
        FalaciaType.APPEAL_TO_MAJORITY: [
            (r'\b(quase )?todos\b', None),
            (r'\ba maioria\b', None),
            (r'\b(ninguém|nenhum)\b', None),
            (r'\bcerteza que\b', None),
        ],
        FalaciaType.CAUSAL_FALLACY: [
            (r'\bportanto\b', None),
            (r'\bconsequentemente\b', None),
            (r'\bdaí\b', None),
            (r'\bpor isso\b', None),
            (r'\bcomo resultado\b', None),
            (r'\bde forma que\b', None),
        ],
        FalaciaType.STRAWMAN: [
            (r'\bo que quer dizer é que\b', None),
            (r'\bassim sendo\b', None),
            (r'\bna prática\b', None),
        ],
        FalaciaType.FALSE_DILEMMA: [
            (r'\bou\b.*\bou\b', None),
            (r'\bapenas\b.*\bou\b', None),
            (r'\bsó há\b', None),
        ],
        FalaciaType.CIRCULAR_REASONING: [
            (r'\bporque\b.*\b porque\b', None),
            (r'\bdevido a\b.*\bdevido a\b', None),
        ],
    }

    SEVERITY_BY_TYPE = {
        FalaciaType.CONTRADICTION: FalaciaSeverity.BLOCKING,
        FalaciaType.GENERALIZATION: FalaciaSeverity.WARNING,
        FalaciaType.APPEAL_TO_AUTHORITY: FalaciaSeverity.WARNING,
        FalaciaType.APPEAL_TO_MAJORITY: FalaciaSeverity.WARNING,
        FalaciaType.CAUSAL_FALLACY: FalaciaSeverity.WARNING,
        FalaciaType.STRAWMAN: FalaciaSeverity.BLOCKING,
        FalaciaType.FALSE_DILEMMA: FalaciaSeverity.WARNING,
        FalaciaType.CIRCULAR_REASONING: FalaciaSeverity.BLOCKING,
    }

    @classmethod
    def detect_falacias(cls, claims: List[ArticleClaim]) -> List[FalaciaCreate]:
        """
        Detect fallacies in a list of claims.

        Returns list of potential fallacies to review.
        """
        detected = []
        claim_texts = [c.claim_text.lower() for c in claims]

        for i, claim in enumerate(claims):
            for falacia_type, patterns in cls.PATTERNS.items():
                for pattern_pair in patterns:
                    if cls._match_pattern(claim.claim_text, pattern_pair):
                        severity = cls.SEVERITY_BY_TYPE.get(falacia_type, FalaciaSeverity.WARNING)

                        related_claim_id = None
                        if i > 0:
                            related_claim_id = claims[i - 1].id

                        detected.append(FalaciaCreate(
                            article_id=claim.article_id,
                            claim_1_id=related_claim_id,
                            claim_2_id=claim.id,
                            falacia_type=falacia_type,
                            severity=severity,
                            description=cls._generate_description(falacia_type, claim.claim_text),
                        ))
                        break

        cls._detect_contradictions(claims, detected)
        cls._detect_m4_issues(claims, detected)

        return detected

    @classmethod
    def _match_pattern(cls, text: str, pattern_pair: Tuple) -> bool:
        """Check if text matches a pattern pair."""
        import re

        text_lower = text.lower()

        if pattern_pair[1] is None:
            return bool(re.search(pattern_pair[0], text_lower, re.IGNORECASE))
        else:
            return bool(re.search(pattern_pair[0], text_lower, re.IGNORECASE) and
                       re.search(pattern_pair[1], text_lower, re.IGNORECASE))

    @classmethod
    def _detect_contradictions(cls, claims: List[ArticleClaim], detected: List):
        """Detect contradictions between pairs of claims."""
        negation_words = ['não', 'nunca', 'nem', 'nenhum', 'ninguém', 'zero']
        positive_words = ['todos', 'sempre', 'algum', 'muitos', 'pode', 'é']

        for i, claim1 in enumerate(claims):
            for claim2 in claims[i + 1:]:
                text1_lower = claim1.claim_text.lower()
                text2_lower = claim2.claim_text.lower()

                has_negation1 = any(w in text1_lower for w in negation_words)
                has_negation2 = any(w in text2_lower for w in negation_words)
                has_positive1 = any(w in text1_lower for w in positive_words)
                has_positive2 = any(w in text2_lower for w in positive_words)

                if (has_negation1 and has_positive2) or (has_positive1 and has_negation2):
                    if cls._shares_subject(text1_lower, text2_lower):
                        detected.append(FalaciaCreate(
                            article_id=claim1.article_id,
                            claim_1_id=claim1.id,
                            claim_2_id=claim2.id,
                            falacia_type=FalaciaType.CONTRADICTION,
                            severity=FalaciaSeverity.BLOCKING,
                            description=f"Contradição: '{claim1.claim_text[:50]}...' vs '{claim2.claim_text[:50]}...'",
                        ))

    @classmethod
    def _shares_subject(cls, text1: str, text2: str) -> bool:
        """Check if two texts share a subject."""
        words1 = set(text1.split()[:10])
        words2 = set(text2.split()[:10])
        common = words1 & words2
        return len(common) >= 3

    @classmethod
    def _detect_m4_issues(cls, claims: List[ArticleClaim], detected: List):
        """Detect issues with M4 (doubtful) claims."""
        for claim in claims:
            if claim.gmif_level == GMIFLevel.M4:
                if any(word in claim.claim_text.lower() for word in ['provavelmente', 'talvez', 'pode ser']):
                    if 'estudos mostram' in claim.claim_text.lower() or 'evidências sugerem' in claim.claim_text.lower():
                        detected.append(FalaciaCreate(
                            article_id=claim.article_id,
                            claim_1_id=claim.id,
                            claim_2_id=None,
                            falacia_type=FalaciaType.APPEAL_TO_AUTHORITY,
                            severity=FalaciaSeverity.WARNING,
                            description=f"Claim M4 usa linguagem de certeza: '{claim.claim_text[:50]}...'",
                        ))

    @classmethod
    def _generate_description(cls, falacia_type: FalaciaType, claim_text: str) -> str:
        """Generate a description for a detected fallacy."""
        descriptions = {
            FalaciaType.CONTRADICTION: f"Contradição lógica detetada em: '{claim_text[:60]}...'",
            FalaciaType.GENERALIZATION: f"Generalização excessiva em: '{claim_text[:60]}...'",
            FalaciaType.APPEAL_TO_AUTHORITY: f"Apelo à autoridade não verificado: '{claim_text[:60]}...'",
            FalaciaType.APPEAL_TO_MAJORITY: f"Apelo à maioria sem evidência: '{claim_text[:60]}...'",
            FalaciaType.CAUSAL_FALLACY: f"Fallácia causal (correlação vs causação): '{claim_text[:60]}...'",
            FalaciaType.STRAWMAN: f"Strawman (deturpação de argumento): '{claim_text[:60]}...'",
            FalaciaType.FALSE_DILEMMA: f"Falso dilema (duas opções quando há mais): '{claim_text[:60]}...'",
            FalaciaType.CIRCULAR_REASONING: f"Raciocínio circular: '{claim_text[:60]}...'",
            FalaciaType.UNKNOWN: f"Falácia desconhecida: '{claim_text[:60]}...'",
        }
        return descriptions.get(falacia_type, descriptions[FalaciaType.UNKNOWN])


class FalaciaPropagator:
    """
    Propagates falacias recursively to all affected islands.

    When a falacia is detected, this service:
    1. Finds all islands/claims that reference the affected content
    2. Marks them as affected
    3. Notifies (or queues notification for) the owners
    """

    def __init__(self):
        self._affected_ilhas: Set[str] = set()
        self._affected_claims: Set[str] = set()
        self._affected_shadow_docs: Set[str] = set()

    def propagate(
        self,
        falacia_id: str,
        claim_ids: List[str],
        article_id: str,
        all_articles_claims: Dict[str, List[ArticleClaim]],
    ) -> Dict[str, Any]:
        """
        Propagate a falacia to all related content.

        Args:
            falacia_id: The detected falacia ID
            claim_ids: IDs of claims involved in the falacia
            article_id: Article containing the claims
            all_articles_claims: Dict mapping article_id -> claims

        Returns:
            Propagation result with affected items
        """
        self._affected_ilhas.clear()
        self._affected_claims.clear()
        self._affected_shadow_docs.clear()

        affected_claims = set(claim_ids)

        for other_article_id, other_claims in all_articles_claims.items():
            if other_article_id == article_id:
                continue

            for claim in other_claims:
                if self._is_related_claim(claim, claim_ids):
                    affected_claims.add(claim.id)

                    if claim.source_shadow_doc_id:
                        self._affected_shadow_docs.add(claim.source_shadow_doc_id)

        return {
            "falacia_id": falacia_id,
            "affected_claims": list(affected_claims),
            "affected_ilhas": list(self._affected_ilhas),
            "affected_shadow_docs": list(self._affected_shadow_docs),
            "total_affected": len(affected_claims),
        }

    def _is_related_claim(self, claim: ArticleClaim, target_ids: List[str]) -> bool:
        """Check if a claim is related to the target claims."""
        target_set = set(target_ids)

        if claim.id in target_set:
            return True

        if claim.source_shadow_doc_id and claim.source_shadow_doc_id in self._affected_shadow_docs:
            return True

        return False


class FalaciaCorrector:
    """
    Suggests corrections for detected fallacies.
    """

    SUGGESTIONS = {
        FalaciaType.CONTRADICTION: "Verificar qual das afirmações está correta. Se ambas forem verdadeiras em contextos diferentes, qualificar com 'em contexto X'.",
        FalaciaType.GENERALIZATION: "Adicionar qualificações: 'alguns', 'muitos', 'frequentemente', 'em condições específicas'.",
        FalaciaType.APPEAL_TO_AUTHORITY: "Adicionar fonte primária verificada. Citar o estudo ou relatório específico.",
        FalaciaType.APPEAL_TO_MAJORITY: "Substituir por dados quantitativos: 'X% de Y' ou 'a maioria de Z (n=n)'.",
        FalaciaType.CAUSAL_FALLACY: "Usar linguagem de correlação: 'A está associado a B', não 'A causa B'.",
        FalaciaType.STRAWMAN: "Representar o argumento original de forma fiel antes de responder.",
        FalaciaType.FALSE_DILEMMA: "Apresentar todas as opções possíveis, não apenas duas.",
        FalaciaType.CIRCULAR_REASONING: "Usar evidência externa para apoiar a conclusão.",
    }

    @classmethod
    def suggest_correction(cls, falacia_type: FalaciaType) -> str:
        """Get a correction suggestion for a falacia type."""
        return cls.SUGGESTIONS.get(
            falacia_type,
            "Revisar a claim e verificar se a lógica está correta."
        )

    @classmethod
    def generate_corrected_claim(cls, claim_text: str, falacia_type: FalaciaType) -> str:
        """Generate a corrected version of a claim."""
        if falacia_type == FalaciaType.GENERALIZATION:
            if 'todos' in claim_text.lower():
                return claim_text.lower().replace('todos', 'muitos').replace('todas as', 'algumas')
            if 'sempre' in claim_text.lower():
                return claim_text.lower().replace('sempre', 'frequentemente')
            if 'nunca' in claim_text.lower():
                return claim_text.lower().replace('nunca', 'raramente')

        if falacia_type == FalaciaType.CAUSAL_FALLACY:
            if 'portanto' in claim_text.lower():
                return claim_text.lower().replace('portanto', 'associado a')
            if 'consequentemente' in claim_text.lower():
                return claim_text.lower().replace('consequentemente', 'em paralelo com')

        if falacia_type == FalaciaType.APPEAL_TO_MAJORITY:
            return claim_text.lower().replace('todos dizem', 'alguns estudos sugerem')

        return f"[REVISAR] {claim_text}"