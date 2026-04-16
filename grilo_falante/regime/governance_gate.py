"""
Governance Gate — Verificação completa de claims

Este módulo implementa o governance gate completo que:
1. Verifica claims contra regras de epistemicidade
2. Usa PINA para decisões normativas
3. Identifica quando intervenção humana é necessária
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class GovernanceResult:
    """Resultado de uma verificação de governance."""
    passed: bool
    blocked_claims: List[Dict]
    warnings: List[str]
    pina_candidates: List[Dict]


class GovernanceGate:
    """
    Governance Gate completo.

    Verifica:
    1. Claims sem fonte quando requerem (M5+)
    2. Contradições com claims existentes
    3. Linguagem de fluência
    4. Proposta PINA para decisions normativas
    """

    def __init__(self, pina_protocol=None):
        self.pina = pina_protocol
        self._validated_claims: List[Dict] = []

    def verify(self, claims: List[Dict]) -> GovernanceResult:
        """
        Verificar claims contra governance gate.

        Args:
            claims: Lista de claims para verificar

        Returns:
            GovernanceResult com resultado completo
        """
        blocked = []
        warnings = []
        pina_candidates = []

        for claim in claims:
            issues = []
            gmif_level = claim.get("gmif_level", "M3")
            text = claim.get("text", "")
            source = claim.get("source")

            # 1. Níveis M5+ requerem fonte
            if gmif_level in ["M5", "M6", "M7"]:
                if not source:
                    issues.append("nível M5+ requer fonte")

            # 2. Nível M7 requer evidência forte
            if gmif_level == "M7":
                if not source:
                    issues.append("M7 requer fonte autoritativa")

            # 3. Contradições
            if self._contradiz_existing(text):
                issues.append("contradiz claim existente")

            # 4. Linguagem de fluência (warning, não block)
            text_lower = text.lower()
            fluency_words = ["obviamente", "claramente", "é óbvio", "é evidente que", "naturalmente"]
            if any(word in text_lower for word in fluency_words):
                warnings.append(f"Fluency detected: {text[:50]}")

            # 5. Claims muito curtas
            if len(text) < 20 and gmif_level not in ["M1", "M2"]:
                issues.append("claim demasiado curta")

            # 6. PINA: decisions normativas requerem proposta
            if self._is_normative_decision(claim):
                pina_candidate = self._create_pina_candidate(claim)
                if pina_candidate:
                    pina_candidates.append(pina_candidate)
                issues.append("PINA required for normative decision")

            if issues:
                blocked.append({
                    "claim_id": claim.get("id", "unknown"),
                    "text": text[:100],
                    "gmif_level": gmif_level,
                    "issues": issues,
                })

        return GovernanceResult(
            passed=len(blocked) == 0 and len(pina_candidates) == 0,
            blocked_claims=blocked,
            warnings=warnings,
            pina_candidates=pina_candidates,
        )

    def _contradiz_existing(self, text: str) -> bool:
        """Verificar contradição com claims existentes."""
        if not self._validated_claims:
            return False

        text_lower = text.lower()
        negations = ["não é", "não existe", "não há", "nunca", "jamais"]

        has_negation = any(neg in text_lower for neg in negations)
        if not has_negation:
            return False

        words_new = set(text_lower.split())
        for existing in self._validated_claims:
            existing_text = existing.get("text", "").lower()
            has_existing_negation = any(neg in existing_text for neg in negations)
            if has_existing_negation:
                continue

            words_existing = set(existing_text.split())
            overlap = words_new & words_existing
            if len(overlap) > 3:
                return True

        return False

    def _is_normative_decision(self, claim: Dict) -> bool:
        """Determinar se claim requer PINA."""
        text_lower = claim.get("text", "").lower()

        normative_indicators = [
            "deve ser", "deveria ser", "deverá ser",
            "é obrigatório", "é necessário",
            "não é permitido", "é proibido",
            "é recomendado", "recomenda-se",
        ]

        return any(ind in text_lower for ind in normative_indicators)

    def _create_pina_candidate(self, claim: Dict) -> Optional[Dict]:
        """Criar candidato PINA."""
        if not self.pina:
            return None

        return {
            "nca_id": f"NCA-{claim.get('id', 'unknown')}",
            "source_document": claim.get("source", "chat"),
            "faithful_statement": claim.get("text", ""),
            "location": "chat",
            "gmif_level": claim.get("gmif_level", "M3"),
        }

    def add_validated_claim(self, claim: Dict) -> None:
        """Adicionar claim validada ao conjunto de referência."""
        if claim.get("legitimacy") == "ASSERTED":
            self._validated_claims.append(claim)

    def get_pina_proposals(self) -> List[Dict]:
        """Obter lista de proposals PINA pendentes."""
        if not self.pina:
            return []
        return [
            {"nca_id": nca.nca_id, "statement": nca.faithful_statement}
            for nca in self.pina._candidates.values()
            if nca.decision is None
        ]
