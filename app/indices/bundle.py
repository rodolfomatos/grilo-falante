"""
Bundle de Reentrada - Pacote para retomar trabalho

Quando o sistema quer responder ou estudar um problema,
pode construir um bundle que reúna:

- Os tópicos certos
- As perguntas operativas certas
- Os artefactos centrais
- As claims associadas
- As fontes relevantes
- Os conflitos e lacunas

Isto aproxima o sistema de uma verdadeira máquina de reentrada cognitiva.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from app.ontology.ilhas import Ilha
from app.indices.canonico import get_indice_canonico
from app.indices.pragmatico import get_indice_pragmatico
from app.indices.coverage import get_coverage_map

logger = logging.getLogger(__name__)


@dataclass
class BundleReentradaCompleto:
    """
    Bundle completo de reentrada para uma tarefa.

    Reúne tudo o que é necessário para continuar o trabalho.
    """
    tarefa: str

    # Tópicos
    tópicos_relevantes: List[Dict[str, Any]] = field(default_factory=list)

    # Ilhas
    ilhas: List[Dict[str, Any]] = field(default_factory=list)

    # Claims
    claims: List[Dict[str, Any]] = field(default_factory=list)

    # Fontes
    fontes: List[Dict[str, Any]] = field(default_factory=list)

    # Lacunas identificadas
    lacunas: List[str] = field(default_factory=list)

    # Conflitos
    conflitos: List[str] = field(default_factory=list)

    # Metadados
    ilhas_count: int = 0
    claims_count: int = 0
    fontes_count: int = 0

    def para_dict(self) -> Dict[str, Any]:
        return {
            "tarefa": self.tarefa,
            "tópicos": self.tópicos_relevantes,
            "ilhas": self.ilhas,
            "claims": self.claims,
            "fontes": self.fontes,
            "lacunas": self.lacunas,
            "conflitos": self.conflitos,
            "stats": {
                "ilhas": self.ilhas_count,
                "claims": self.claims_count,
                "fontes": self.fontes_count,
            },
        }


class ConstrutorBundle:
    """
    Construtor de bundles de reentrada.

    Usa os índices (canónico, pragmático, coverage) para construir
    um bundle completo para uma tarefa.
    """

    def __init__(self):
        self.indice_canonico = get_indice_canonico()
        self.indice_pragmatico = get_indice_pragmatico()
        self.coverage_map = get_coverage_map()

    def construir(
        self,
        tarefa: str,
        ilhas: List[Ilha],
        claims: Optional[List[Dict[str, Any]]] = None,
        max_ilhas: int = 5,
        max_claims: int = 10,
    ) -> BundleReentradaCompleto:
        """
        Construir bundle de reentrada para uma tarefa.

        Args:
            tarefa: Descrição da tarefa/pergunta
            ilhas: Lista de ilhas disponíveis
            claims: Lista de claims (opcional)
            max_ilhas: Máximo de ilhas a incluir
            max_claims: Máximo de claims a incluir

        Returns:
            Bundle completo
        """
        bundle = BundleReentradaCompleto(tarefa=tarefa)

        # 1. Encontrar tópicos relevantes
        bundle.tópicos_relevantes = self._encontrar_tópicos(tarefa)

        # 2. Encontrar ilhas relacionadas
        bundle.ilhas = self._encontrar_ilhas(tarefa, ilhas, max_ilhas)
        bundle.ilhas_count = len(bundle.ilhas)

        # 3. Claims das ilhas
        bundle.claims = self._encontrar_claims(bundle.ilhas, claims, max_claims)
        bundle.claims_count = len(bundle.claims)

        # 4. Fontes dos tópicos
        bundle.fontes = self._encontrar_fontes(bundle.tópicos_relevantes)
        bundle.fontes_count = len(bundle.fontes)

        # 5. Lacunas dos tópicos
        bundle.lacunas = self._identificar_lacunas(bundle.tópicos_relevantes)

        # 6. Conflitos (por implementar - precisaria de análise)
        bundle.conflitos = []

        logger.info(
            f"Bundle construído: {bundle.ilhas_count} ilhas, "
            f"{bundle.claims_count} claims, {bundle.fontes_count} fontes"
        )

        return bundle

    def _encontrar_tópicos(
        self,
        tarefa: str,
    ) -> List[Dict[str, Any]]:
        """Encontrar tópicos relevantes para a tarefa."""
        # Buscar no índice pragmático
        entradas = self.indice_pragmatico.buscar_por_tarefa(tarefa)

        tópicos = []
        for entrada in entradas[:5]:
            if entrada.tópico_id:
                tópico = self.indice_canonico.tópicos.get(entrada.tópico_id)
                if tópico:
                    tópicos.append(tópico.para_dict())

        # Se não encontrou, buscar no índice canónico
        if not tópicos:
            resultados = self.indice_canonico.buscar_por_tópico(tarefa)
            tópicos = [t.para_dict() for t in resultados[:5]]

        return tópicos

    def _encontrar_ilhas(
        self,
        tarefa: str,
        ilhas: List[Ilha],
        max_ilhas: int,
    ) -> List[Dict[str, Any]]:
        """Encontrar ilhas mais relevantes para a tarefa."""
        # Ordenar por score de ativação
        ordenadas = sorted(ilhas, key=lambda i: i.score_ativação, reverse=True)

        # Filtrar por relevância (termenho de match)
        tarefa_lower = tarefa.lower()
        relevantes = []

        for ilha in ordenadas:
            # Verificar se a ilha é relevante
            texto = f"{ilha.nome or ''} {ilha.descrição or ''}".lower()

            # Score de relevância simples
            palavras_tarefa = set(tarefa_lower.split())
            palavras_ilha = set(texto.split())
            overlap = len(palavras_tarefa & palavras_ilha)

            if overlap >= 1 or ilha.score_ativação > 0.7:
                relevantes.append({
                    "id": ilha.id,
                    "nome": ilha.nome or "Sem nome",
                    "descrição": ilha.descrição[:100] if ilha.descrição else "",
                    "score": ilha.score_ativação,
                    "membros_count": len(ilha.membros),
                    "estado": ilha.estado.value,
                })

            if len(relevantes) >= max_ilhas:
                break

        return relevantes

    def _encontrar_claims(
        self,
        ilhas: List[Dict[str, Any]],
        claims: Optional[List[Dict[str, Any]]],
        max_claims: int,
    ) -> List[Dict[str, Any]]:
        """Encontrar claims das ilhas."""
        if not claims:
            return []

        # Filtrar claims das ilhas relevantes
        ilha_ids = {i["id"] for i in ilhas}

        claims_filtradas = [
            c for c in claims
            if c.get("ilha_id") in ilha_ids
        ][:max_claims]

        return claims_filtradas

    def _encontrar_fontes(
        self,
        tópicos: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Encontrar fontes para os tópicos."""
        fontes = []

        for tópico in tópicos:
            tópico_id = tópico.get("id")
            if not tópico_id:
                continue

            coberturas = self.coverage_map.fontes_para_tópico(tópico_id)

            for c in coberturas[:2]:  # Máximo 2 por tópico
                fontes.append({
                    "fonte_id": c.fonte_id,
                    "fonte_nome": c.fonte_nome,
                    "páginas": c.páginas,
                    "qualidade": c.qualidade,
                })

        return fontes[:10]  # Máximo 10 total

    def _identificar_lacunas(
        self,
        tópicos: List[Dict[str, Any]],
    ) -> List[str]:
        """Identificar lacunas nos tópicos."""
        lacunas = []

        for tópico in tópicos:
            tópico_id = tópico.get("id")
            if not tópico_id:
                continue

            score = self.coverage_map.score_cobertura(tópico_id)
            if score < 0.3:
                lacunas.append(
                    f"Tópico '{tópico.get('nome', tópico_id)}' com cobertura insuficiente ({score:.2f})"
                )

        return lacunas


def construir_bundle(
    tarefa: str,
    ilhas: List[Ilha],
    claims: Optional[List[Dict[str, Any]]] = None,
) -> BundleReentradaCompleto:
    """
    Função de conveniência para construir bundle.

    Args:
        tarefa: Tarefa/pergunta
        ilhas: Lista de ilhas
        claims: Lista de claims (opcional)

    Returns:
        Bundle de reentrada
    """
    construtor = ConstrutorBundle()
    return construtor.construir(tarefa, ilhas, claims)
