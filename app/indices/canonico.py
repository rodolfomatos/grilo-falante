"""
Índice Canónico - Índice primário baseado em tópicos do domínio

O índice canónico é uma estrutura estável de tópicos do domínio.
Não é improvisado a cada interação. Serve como mapa de topo.

Este módulo implementa:
- Definição de tópicos canónicos
- Mapeamento de ilhas para tópicos
- Busca por tópico
"""

import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field

from app.ontology.ilhas import Ilha

logger = logging.getLogger(__name__)


@dataclass
class TopicoCanonico:
    """
    Um tópico canónico no índice primário.

    Cada tópico representa uma entrada estável no mapa de topo.
    """
    id: str
    nome: str
    descrição: str = ""
    tópicos_filhos: List[str] = field(default_factory=list)
    tópicos_pai: Optional[str] = None

    # Metadados
    created_at: str = ""
    updated_at: str = ""

    def para_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "nome": self.nome,
            "descrição": self.descrição,
            "filhos": self.tópicos_filhos,
            "pai": self.tópicos_pai,
        }


class IndiceCanonico:
    """
    Índice Canónico - estrutura estável de tópicos do domínio.

    O índice canónico é ancorado no programa/disciplina oficial.
    Cada entrada representa um tópico canónico, não improvisado.
    """

    def __init__(self):
        self.tópicos: Dict[str, TopicoCanonico] = {}
        self._ilha_para_tópico: Dict[str, str] = {}

    def adicionar_tópico(self, tópico: TopicoCanonico) -> None:
        """Adicionar um tópico ao índice."""
        self.tópicos[tópico.id] = tópico
        logger.debug(f"Adicionado tópico canónico: {tópico.id}")

    def mapear_ilha(
        self,
        ilha_id: str,
        tópico_id: str,
    ) -> None:
        """
        Mapear uma ilha para um tópico canónico.

        Args:
            ilha_id: ID da ilha
            tópico_id: ID do tópico
        """
        if tópico_id not in self.tópicos:
            logger.warning(f"Tópico {tópico_id} não existe")
            return

        self._ilha_para_tópico[ilha_id] = tópico_id
        logger.debug(f"Ilha {ilha_id} mapeada para tópico {tópico_id}")

    def obter_tópico_da_ilha(self, ilha_id: str) -> Optional[TopicoCanonico]:
        """Obter o tópico canónico de uma ilha."""
        tópico_id = self._ilha_para_tópico.get(ilha_id)
        if not tópico_id:
            return None
        return self.tópicos.get(tópico_id)

    def obter_ilhas_do_tópico(
        self,
        tópico_id: str,
    ) -> List[str]:
        """Obter IDs das ilhas mapeadas para um tópico."""
        return [
            ilha_id for ilha_id, tid in self._ilha_para_tópico.items()
            if tid == tópico_id
        ]

    def buscar_por_tópico(self, query: str) -> List[TopicoCanonico]:
        """
        Buscar tópicos por query.

        Args:
            query: String de busca

        Returns:
            Lista de tópicos que matcham
        """
        query_lower = query.lower()
        resultados = []

        for tópico in self.tópicos.values():
            if query_lower in tópico.nome.lower():
                resultados.append(tópico)
            elif query_lower in tópico.descrição.lower():
                resultados.append(tópico)

        return resultados

    def listar_tópicos(self) -> List[TopicoCanonico]:
        """Listar todos os tópicos canónicos."""
        return list(self.tópicos.values())

    def listar_tópicos_raiz(self) -> List[TopicoCanonico]:
        """Listar tópicos de topo (sem pai)."""
        return [t for t in self.tópicos.values() if t.tópicos_pai is None]

    def obter_subárvore(
        self,
        tópico_id: str,
    ) -> List[TopicoCanonico]:
        """Obter um tópico e todos os seus descendentes."""
        if tópico_id not in self.tópicos:
            return []

        resultado = [self.tópicos[tópico_id]]
        tópico = self.tópicos[tópico_id]

        for filho_id in tópico.tópicos_filhos:
            resultado.extend(self.obter_subárvore(filho_id))

        return resultado


# Índice global singleton
_indice: Optional[IndiceCanonico] = None


def get_indice_canonico() -> IndiceCanonico:
    """Obter instância global do índice canónico."""
    global _indice
    if _indice is None:
        _indice = IndiceCanonico()
        _inicializar_padrão(_indice)
    return _indice


def _inicializar_padrão(indice: IndiceCanonico) -> None:
    """Inicializar com tópicos padrão do domínio Grilo Falante."""
    padrão = [
        TopicoCanonico(
            id="governance",
            nome="Governança Epistémica",
            descrição="Regime, gates, promoção, bloqueio",
        ),
        TopicoCanonico(
            id="governance-regime",
            nome="Regime Normativo",
            descrição="ACORDAR, DORMIR, LOAD, estado do regime",
            tópicos_pai="governance",
        ),
        TopicoCanonico(
            id="governance-audit",
            nome="Auditoria Hostil",
            descrição="Auditoria, verificação, validação",
            tópicos_pai="governance",
        ),
        TopicoCanonico(
            id="memory",
            nome="Memória e Arquitetura",
            descrição="Memória, recuperação, evocação",
        ),
        TopicoCanonico(
            id="memory-insular",
            nome="Memória Insular",
            descrição="Ilhas, pedras, saliência, erosão",
            tópicos_pai="memory",
        ),
        TopicoCanonico(
            id="memory-layers",
            nome="Camadas de Memória",
            descrição="MemPalace, PostgreSQL, ledger",
            tópicos_pai="memory",
        ),
        TopicoCanonico(
            id="gmif",
            nome="GMIF",
            descrição="Graphical Meta-Information Framework, M1-M7",
        ),
        TopicoCanonico(
            id="claims",
            nome="Claims e Claims",
            descrição="Extração, classificação, validação de claims",
        ),
        TopicoCanonico(
            id="evidence",
            nome="Evidência",
            descrição="Fontes, proveniência, evidências",
            tópicos_pai="claims",
        ),
        TopicoCanonico(
            id="epistemology",
            nome="Epistemologia",
            descrição="Legitimidade, correção factual, promoção",
        ),
        TopicoCanonico(
            id="tools",
            nome="Ferramentas e Interface",
            descrição="MCP tools, CLI, API, Chat",
        ),
        TopicoCanonico(
            id="implementation",
            nome="Implementação",
            descrição="Código, arquitetura, deployment",
        ),
    ]

    for tópico in padrão:
        indice.adicionar_tópico(tópico)
