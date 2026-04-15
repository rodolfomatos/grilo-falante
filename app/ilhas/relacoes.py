"""
Relações entre Ilhas - Conexões e similaridades

Este módulo gere as relações entre ilhas:
- Encontrar ilhas relacionadas
- Calcular similaridade
- Sugerir agregações
- Criar e manter relações
"""

import logging
from typing import List, Dict, Any, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from app.ontology.ilhas import Ilha

from app.ontology.ilhas import RelacaoIlha, Saliencia
from app.ontology.estados import TipoRelacao
from grilo_falante.backend.db.ilhas_repository import IlhaRepository
from grilo_falante.backend.memory.mempalace_ilhas import MemPalaceIlhas

logger = logging.getLogger(__name__)


class CalculadorSimilaridade:
    """
    Calcula similaridade entre ilhas.

    Usa múltiplos critérios:
    - Conteúdo textual (TF-IDF simplificado)
    - Membros em comum
    - Embeddings (se disponível)
    """

    PESOS_SIMILARIDADE = {
        "conteúdo": 0.4,
        "membros": 0.3,
        "topicos": 0.3,
    }

    def __init__(
        self,
        mempalace: Optional[MemPalaceIlhas] = None,
    ):
        self.mempalace = mempalace

    def calcular(
        self,
        ilha1: "Ilha",
        ilha2: "Ilha",
    ) -> float:
        """
        Calcular similaridade entre duas ilhas.

        Args:
            ilha1: Primeira ilha
            ilha2: Segunda ilha

        Returns:
            Score de similaridade (0-1)
        """
        scores = []

        # Similaridade de conteúdo
        sim_conteudo = self._similaridade_conteúdo(ilha1, ilha2)
        scores.append(("conteúdo", sim_conteudo, self.PESOS_SIMILARIDADE["conteúdo"]))

        # Similaridade de membros
        sim_membros = self._similaridade_membros(ilha1, ilha2)
        scores.append(("membros", sim_membros, self.PESOS_SIMILARIDADE["membros"]))

        # Similaridade de tópicos (nomes/descrições)
        sim_topicos = self._similaridade_topicos(ilha1, ilha2)
        scores.append(("topicos", sim_topicos, self.PESOS_SIMILARIDADE["topicos"]))

        # Média ponderada
        total_peso = sum(s[2] for s in scores)
        similaridade = sum(s[1] * s[2] for s in scores) / total_peso

        return similaridade

    def _similaridade_conteúdo(
        self,
        ilha1: "Ilha",
        ilha2: "Ilha",
    ) -> float:
        """Similaridade baseada em conteúdo textual."""
        texto1 = f"{ilha1.nome or ''} {ilha1.descrição or ''}".lower()
        texto2 = f"{ilha2.nome or ''} {ilha2.descrição or ''}".lower()

        if not texto1 or not texto2:
            return 0.0

        palavras1 = set(texto1.split())
        palavras2 = set(texto2.split())

        if not palavras1 or not palavras2:
            return 0.0

        intersecção = len(palavras1 & palavras2)
        união = len(palavras1 | palavras2)

        return intersecção / união if união > 0 else 0.0

    def _similaridade_membros(
        self,
        ilha1: "Ilha",
        ilha2: "Ilha",
    ) -> float:
        """Similaridade baseada em membros partilhados."""
        membros1 = {m.member_id for m in ilha1.membros}
        membros2 = {m.member_id for m in ilha2.membros}

        if not membros1 or not membros2:
            return 0.0

        intersecção = len(membros1 & membros2)
        união = len(membros1 | membros2)

        return intersecção / união if união > 0 else 0.0

    def _similaridade_topicos(
        self,
        ilha1: "Ilha",
        ilha2: "Ilha",
    ) -> float:
        """Similaridade baseada em tópicos (simplificado)."""
        # Usa lacunas_identificadas como proxy para tópicos
        topicos1 = set(ilha1.lacunas_identificadas)
        topicos2 = set(ilha2.lacunas_identificadas)

        if not topicos1 or not topicos2:
            return 0.0

        intersecção = len(topicos1 & topicos2)
        união = len(topicos1 | topicos2)

        return intersecção / união if união > 0 else 0.0


class GestorRelações:
    """
    Gestor de relações entre ilhas.

    Permite criar, listar e gerir relações entre ilhas.
    """

    def __init__(
        self,
        repo: Optional[IlhaRepository] = None,
        mempalace: Optional[MemPalaceIlhas] = None,
        calculador: Optional[CalculadorSimilaridade] = None,
    ):
        self.repo = repo or IlhaRepository()
        self.mempalace = mempalace or MemPalaceIlhas()
        self.calculador = calculador or CalculadorSimilaridade(mempalace)

    async def criar_relação(
        self,
        ilha1_id: str,
        ilha2_id: str,
        tipo: TipoRelacao,
        força: float = 0.5,
    ) -> bool:
        """
        Criar uma relação entre duas ilhas.

        Args:
            ilha1_id: ID da primeira ilha
            ilha2_id: ID da segunda ilha
            tipo: Tipo de relação
            força: Força da relação (0-1)

        Returns:
            True se criada com sucesso
        """
        ilha1 = await self.repo.obter(ilha1_id)
        if not ilha1:
            return False

        # Verificar se já existe relação
        if ilha1.tem_relação(ilha2_id):
            logger.debug(f"Relação já existe entre {ilha1_id} e {ilha2_id}")
            return True

        # Adicionar relação
        relação = RelacaoIlha(
            ilha_id=ilha2_id,
            tipo=tipo,
            força=força,
        )
        ilha1.adicionar_relação(relação)

        await self.repo.atualizar(ilha1)

        # Também guardar no MemPalace
        await self.mempalace.adicionar_relação_ilha(
            ilha1_id, ilha2_id, tipo.value, força
        )

        logger.info(f"Criada relação {tipo.value} ({força:.2f}) entre {ilha1_id} e {ilha2_id}")
        return True

    async def remover_relação(
        self,
        ilha1_id: str,
        ilha2_id: str,
    ) -> bool:
        """
        Remover relação entre duas ilhas.

        Args:
            ilha1_id: ID da primeira ilha
            ilha2_id: ID da segunda ilha

        Returns:
            True se removida
        """
        ilha1 = await self.repo.obter(ilha1_id)
        if not ilha1:
            return False

        # Remover relação (criar nova lista sem a relação)
        from app.ontology.ilhas import RelacaoIlha

        novas_relações = [r for r in ilha1.relações if r.ilha_id != ilha2_id]
        ilha1.relações = novas_relações

        await self.repo.atualizar(ilha1)
        return True

    async def encontrar_similares(
        self,
        ilha_id: str,
        limit: int = 5,
        threshold: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """
        Encontrar ilhas similares a uma dada ilha.

        Args:
            ilha_id: ID da ilha de referência
            limit: Número máximo de resultados
            threshold: Score mínimo de similaridade

        Returns:
            Lista de ilhas similares com scores
        """
        ilha = await self.repo.obter(ilha_id)
        if not ilha:
            return []

        todas = await self.repo.listar(limit=100)

        similares = []
        for outra in todas:
            if outra.id == ilha_id:
                continue

            score = self.calculador.calcular(ilha, outra)
            if score >= threshold:
                similares.append({
                    "ilha_id": outra.id,
                    "nome": outra.nome,
                    "score": score,
                    "estado": outra.estado.value,
                })

        # Ordenar por score
        similares.sort(key=lambda x: x["score"], reverse=True)
        return similares[:limit]

    async def sugerir_agregação(
        self,
        threshold_similaridade: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """
        Sugerir ilhas que devem ser agregadas.

        Args:
            threshold_similaridade: Score mínimo para sugerir agregação

        Returns:
            Lista de pares de ilhas para agregar
        """
        ilhas = await self.repo.listar(limit=100)
        sugeridos = []

        # Comparar todas as ilhas duas a duas
        for i, ilha1 in enumerate(ilhas):
            for ilha2 in ilhas[i+1:]:
                score = self.calculador.calcular(ilha1, ilha2)

                if score >= threshold_similaridade:
                    sugeridos.append({
                        "ilha1_id": ilha1.id,
                        "ilha1_nome": ilha1.nome,
                        "ilha2_id": ilha2.id,
                        "ilha2_nome": ilha2.nome,
                        "similaridade": score,
                    })

        # Ordenar por similaridade
        sugeridos.sort(key=lambda x: x["similaridade"], reverse=True)
        return sugeridos

    async def obter_relações_ilha(
        self,
        ilha_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Obter todas as relações de uma ilha.

        Args:
            ilha_id: ID da ilha

        Returns:
            Lista de relações
        """
        ilha = await self.repo.obter(ilha_id)
        if not ilha:
            return []

        relações = []
        for relação in ilha.relações:
            ilha_relacionada = await self.repo.obter(relação.ilha_id)
            relações.append({
                "ilha_id": relação.ilha_id,
                "nome": ilha_relacionada.nome if ilha_relacionada else "Desconhecida",
                "tipo": relação.tipo.value,
                "força": relação.força,
            })

        return relações


async def sugerir_agregações_batch(
    threshold: float = 0.7,
) -> List[Dict[str, Any]]:
    """
    Função de conveniência para sugerir agregações.

    Args:
        threshold: Score mínimo

    Returns:
        Lista de pares sugeridos
    """
    gestor = GestorRelações()
    return await gestor.sugerir_agregação(threshold)
