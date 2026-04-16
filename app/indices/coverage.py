"""
Coverage Map - Mapa de cobertura de tópicos por fontes

O coverage map é uma forma explícita de mapear que fontes,
documentos ou artefactos cobrem determinado tópico ou pergunta.

Permite saber:
- Quais fontes cobrem um tópico?
- Quais tópicos têm cobertura suficiente?
- Quais tópicos têm lacunas?
"""

import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class Cobertura:
    """
    Representa a cobertura de um tópico por uma fonte.
    """
    tópico_id: str
    fonte_id: str
    fonte_nome: str
    páginas: List[str] = field(default_factory=list)
    qualidade: float = 0.5  # 0-1
    relevância: float = 0.5  # 0-1


@dataclass
class Lacuna:
    """
    Representa uma lacuna de cobertura num tópico.
    """
    tópico_id: str
    tópico_nome: str
    descrição: str
    severidade: str = "media"  # baixa, media, alta
    fontes_necessárias: List[str] = field(default_factory=list)


class CoverageMap:
    """
    Mapa de Coverage - mapear que fontes cobrem que tópicos.

    Permite saber a cobertura de cada tópico e identificar lacunas.
    """

    def __init__(self):
        # tópico_id -> [Cobertura]
        self._cobertura: Dict[str, List[Cobertura]] = {}

        # fonte_id -> [tópico_id]
        self._fonte_para_tópicos: Dict[str, Set[str]] = {}

    def adicionar_cobertura(
        self,
        tópico_id: str,
        fonte_id: str,
        fonte_nome: str,
        páginas: Optional[List[str]] = None,
        qualidade: float = 0.5,
        relevância: float = 0.5,
    ) -> None:
        """
        Adicionar cobertura de uma fonte a um tópico.

        Args:
            tópico_id: ID do tópico
            fonte_id: ID da fonte
            fonte_nome: Nome descritivo da fonte
            páginas: Lista de páginas/secções
            qualidade: Qualidade da fonte (0-1)
            relevância: Relevância para o tópico (0-1)
        """
        cobertura = Cobertura(
            tópico_id=tópico_id,
            fonte_id=fonte_id,
            fonte_nome=fonte_nome,
            páginas=páginas or [],
            qualidade=qualidade,
            relevância=relevância,
        )

        if tópico_id not in self._cobertura:
            self._cobertura[tópico_id] = []

        # Verificar se já existe
        existente = None
        for c in self._cobertura[tópico_id]:
            if c.fonte_id == fonte_id:
                existente = c
                break

        if existente:
            # Atualizar
            existente.páginas.extend(páginas or [])
            existente.qualidade = qualidade
            existente.relevância = relevância
        else:
            self._cobertura[tópico_id].append(cobertura)

        # Atualizar índice fonte→tópicos
        if fonte_id not in self._fonte_para_tópicos:
            self._fonte_para_tópicos[fonte_id] = set()
        self._fonte_para_tópicos[fonte_id].add(tópico_id)

        logger.debug(f"Adicionada cobertura {fonte_nome} → {tópico_id}")

    def fontes_para_tópico(self, tópico_id: str) -> List[Cobertura]:
        """
        Obter todas as fontes que cobrem um tópico.

        Args:
            tópico_id: ID do tópico

        Returns:
            Lista de coberturas ordenadas por relevância
        """
        coberturas = self._cobertura.get(tópico_id, [])
        return sorted(coberturas, key=lambda c: c.relevância * c.qualidade, reverse=True)

    def tópicos_da_fonte(self, fonte_id: str) -> List[str]:
        """Obter todos os tópicos cobertos por uma fonte."""
        return list(self._fonte_para_tópicos.get(fonte_id, set()))

    def score_cobertura(self, tópico_id: str) -> float:
        """
        Calcular score de cobertura de um tópico.

        Args:
            tópico_id: ID do tópico

        Returns:
            Score entre 0-1
        """
        coberturas = self._cobertura.get(tópico_id, [])
        if not coberturas:
            return 0.0

        # Média ponderada de qualidade × relevância
        total = sum(c.qualidade * c.relevância for c in coberturas)
        return min(1.0, total / len(coberturas))

    def identificar_lacunas(
        self,
        tópicos: List[str],
        threshold: float = 0.3,
    ) -> List[Lacuna]:
        """
        Identificar lacunas de cobertura.

        Args:
            tópicos: Lista de tópicos a verificar
            threshold: Score abaixo do qual é lacuna

        Returns:
            Lista de lacunas identificadas
        """
        lacunas = []

        for tópico_id in tópicos:
            score = self.score_cobertura(tópico_id)
            if score < threshold:
                lacunas.append(Lacuna(
                    tópico_id=tópico_id,
                    tópico_nome=tópico_id,  # Pode ser preenchido depois
                    descrição=f"Cobertura insuficiente: {score:.2f} < {threshold}",
                    severidade="alta" if score < 0.1 else "media",
                ))

        return lacunas

    def cobertura_resumo(self) -> Dict[str, Any]:
        """
        Obter resumo da cobertura do sistema.

        Returns:
            Dict com estatísticas
        """
        total_tópicos = len(self._cobertura)
        total_fontes = len(self._fonte_para_tópicos)

        scores = [self.score_cobertura(t) for t in self._cobertura]
        score_médio = sum(scores) / len(scores) if scores else 0

        return {
            "total_tópicos_com_cobertura": total_tópicos,
            "total_fontes": total_fontes,
            "score_médio": score_médio,
            "tópicos_sem_cobertura": total_tópicos,
        }

    def remover_fonte(self, fonte_id: str) -> None:
        """Remover todas as coberturas de uma fonte."""
        if fonte_id not in self._fonte_para_tópicos:
            return

        tópicos = self._fonte_para_tópicos[fonte_id]
        for tópico_id in tópicos:
            if tópico_id in self._cobertura:
                self._cobertura[tópico_id] = [
                    c for c in self._cobertura[tópico_id]
                    if c.fonte_id != fonte_id
                ]

        del self._fonte_para_tópicos[fonte_id]


# Singleton
_coverage_map: Optional[CoverageMap] = None


def get_coverage_map() -> CoverageMap:
    """Obter instância global do coverage map."""
    global _coverage_map
    if _coverage_map is None:
        _coverage_map = CoverageMap()
    return _coverage_map
