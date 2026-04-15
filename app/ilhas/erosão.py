"""
Dinâmica de Erosão - Decay e gestão de ilhas ao longo do tempo

Este módulo implementa a dinâmica de erosão das ilhas:
- Decay do score de ativação
- Transições de estado (ATIVA → ERODENDO → DORMINTE)
- Reativação de ilhas

Importante: Erosão NÃO significa apagamento. Reduzir prioridade ≠ apagar.
O valor epistémico persiste.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from app.ontology.ilhas import Ilha
from app.ontology.estados import EstadoIlha
from grilo_falante.backend.db.ilhas_repository import IlhaRepository

logger = logging.getLogger(__name__)


class DinâmicaErosão:
    """
    Dinâmica de erosão para ilhas.

    Gere o decay do score de ativação e as transições de estado
    ao longo do tempo, sem apagar ilhas.
    """

    # Thresholds de estado
    THRESHOLD_EROSÃO = 0.1      # Abaixo disto = ERODENDO
    THRESHOLD_HIBERNAÇÃO = 0.01  # Abaixo disto = DORMINTE
    THRESHOLD_CONSOLIDAÇÃO = 0.8  # Acima disto = CONSOLIDADA

    # Decay
    DECAY_FACTOR_DIÁRIO = 0.95
    DIAS_SEM_USO_PARA_EROSÃO = 7
    DIAS_SEM_USO_PARA_HIBERNAÇÃO = 30

    def __init__(
        self,
        repo: Optional[IlhaRepository] = None,
    ):
        self.repo = repo or IlhaRepository()

    async def aplicar_decay_todas(
        self,
        dias: int = 1,
    ) -> Dict[str, int]:
        """
        Aplicar decay a todas as ilhas.

        Args:
            dias: Número de dias desde última atualização

        Returns:
            Dict com contagens de estados alterados
        """
        ilhas = await self.repo.listar(limit=1000)
        estados = {
            "actualizadas": 0,
            "para_erosão": 0,
            "para_hibernação": 0,
            "para_consolidação": 0,
        }

        for ilha in ilhas:
            alterado = await self._aplicar_decay_ilha(ilha, dias)
            if alterado:
                estados["actualizadas"] += 1

        return estados

    async def _aplicar_decay_ilha(
        self,
        ilha: Ilha,
        dias: int,
    ) -> bool:
        """
        Aplicar decay a uma ilha individual.

        Args:
            ilha: Ilha a processar
            dias: Número de dias desde última atualização

        Returns:
            True se alterou algo
        """
        estado_antes = ilha.estado
        score_antes = ilha.score_ativação

        # Aplicar decay exponencial
        factor = self.DECAY_FACTOR_DIÁRIO ** dias
        ilha.score_ativação *= factor

        # Atualizar estado baseado no novo score
        await self._actualizar_estado(ilha)

        # Se mudou estado, guardar
        if ilha.estado != estado_antes or abs(ilha.score_ativação - score_antes) > 0.001:
            await self.repo.atualizar(ilha)
            logger.debug(
                f"Ilha {ilha.id}: score {score_antes:.3f} → {ilha.score_ativação:.3f}, "
                f"estado {estado_antes.value} → {ilha.estado.value}"
            )
            return True

        return False

    async def _actualizar_estado(self, ilha: Ilha) -> None:
        """
        Atualizar estado da ilha baseado no score.

        Args:
            ilha: Ilha a atualizar
        """
        score = ilha.score_ativação

        if score >= self.THRESHOLD_CONSOLIDAÇÃO and len(ilha.membros) >= 10:
            ilha.estado = EstadoIlha.CONSOLIDADA
        elif score < self.THRESHOLD_HIBERNAÇÃO:
            ilha.estado = EstadoIlha.DORMINTE
        elif score < self.THRESHOLD_EROSÃO:
            if ilha.estado != EstadoIlha.DORMINTE:
                ilha.estado = EstadoIlha.ERODENDO
        elif score >= self.THRESHOLD_EROSÃO:
            if ilha.estado in (EstadoIlha.ERODENDO, EstadoIlha.DORMINTE):
                ilha.estado = EstadoIlha.ATIVA

    async def reativar_ilha(
        self,
        ilha_id: str,
        boost: float = 0.2,
    ) -> Optional[Ilha]:
        """
        Reativar uma ilha dormente ou erodindo.

        Args:
            ilha_id: ID da ilha
            boost: Quanto aumentar o score

        Returns:
            Ilha reativada ou None
        """
        ilha = await self.repo.obter(ilha_id)
        if not ilha:
            return None

        # Aumentar score
        ilha.score_ativação = min(1.0, ilha.score_ativação + boost)

        # Voltar a ativa se estava erodindo ou dormente
        if ilha.estado in (EstadoIlha.ERODENDO, EstadoIlha.DORMINTE):
            ilha.estado = EstadoIlha.ATIVA

        await self.repo.atualizar(ilha)
        logger.info(f"Ilha {ilha_id} reativada, novo score: {ilha.score_ativação:.3f}")

        return ilha

    async def calcular_tempo_para_decay(
        self,
        ilha: Ilha,
        target_score: float = 0.1,
    ) -> Optional[int]:
        """
        Calcular quantos dias até uma ilha atingir um dado score.

        Args:
            ilha: Ilha a calcular
            target_score: Score alvo

        Returns:
            Número de dias ou None se já está abaixo
        """
        if ilha.score_ativação <= target_score:
            return 0

        if self.DECAY_FACTOR_DIÁRIO >= 1.0:
            return None  # Não há decay

        # score_atual * factor^dias = score_alvo
        # factor^dias = score_alvo / score_atual
        # dias = log(score_alvo / score_atual) / log(factor)

        import math
        ratio = target_score / ilha.score_ativação
        if ratio <= 0:
            return None

        dias = math.log(ratio) / math.log(self.DECAY_FACTOR_DIÁRIO)
        return int(math.ceil(dias))

    async def get_estatísticas_decay(
        self,
    ) -> Dict[str, Any]:
        """
        Obter estatísticas de decay do sistema.

        Returns:
            Dict com estatísticas
        """
        ilhas = await self.repo.listar(limit=1000)

        por_estado = {
            EstadoIlha.EMBRIONARIA: 0,
            EstadoIlha.ATIVA: 0,
            EstadoIlha.CONSOLIDADA: 0,
            EstadoIlha.ERODENDO: 0,
            EstadoIlha.DORMINTE: 0,
        }

        scores = []
        membros_total = 0

        for ilha in ilhas:
            por_estado[ilha.estado] += 1
            scores.append(ilha.score_ativação)
            membros_total += len(ilha.membros)

        return {
            "total_ilhas": len(ilhas),
            "por_estado": {k.value: v for k, v in por_estado.items()},
            "score_médio": sum(scores) / len(scores) if scores else 0,
            "score_max": max(scores) if scores else 0,
            "score_min": min(scores) if scores else 0,
            "membros_total": membros_total,
            "decay_factor_diário": self.DECAY_FACTOR_DIÁRIO,
        }


class GestorReativações:
    """
    Gestor de reativações de ilhas.

    Regista quando uma ilha é reativada e calcula
    o impacto no score.
    """

    BOOST_REATIVAÇÃO = 0.15
    BOOST_CONSULTA = 0.05
    BOOST_EDIÇÃO = 0.10

    def __init__(
        self,
        repo: Optional[IlhaRepository] = None,
    ):
        self.repo = repo or IlhaRepository()

    async def registar_reativação(
        self,
        ilha_id: str,
        tipo: str = "reativação",
        session_id: str = "",
    ) -> Optional[Ilha]:
        """
        Registar uma reativação de ilha.

        Args:
            ilha_id: ID da ilha
            tipo: Tipo de reativação (reativação, consulta, edição)
            session_id: ID da sessão

        Returns:
            Ilha atualizada ou None
        """
        from app.ontology.ilhas import HistóricoReativacao

        ilha = await self.repo.obter(ilha_id)
        if not ilha:
            return None

        # Calcular boost baseado no tipo
        boost = self._get_boost_por_tipo(tipo)

        # Atualizar score
        ilha.score_ativação = min(1.0, ilha.score_ativação + boost)

        # Actualizar ou criar histórico
        await self.repo.adicionar_reação(
            ilha_id,
            HistóricoReativacao(
                tipo=tipo,
                session_id=session_id,
            ),
        )

        # Se estava dormente/erodindo, voltar a ativa
        if ilha.estado in (EstadoIlha.DORMINTE, EstadoIlha.ERODENDO):
            ilha.estado = EstadoIlha.ATIVA

        await self.repo.atualizar(ilha)

        logger.info(f"Registrada {tipo} em {ilha_id}, boost {boost:.3f}")
        return ilha

    def _get_boost_por_tipo(self, tipo: str) -> float:
        """Obter boost baseado no tipo de reativação."""
        boosts = {
            "reativação": self.BOOST_REATIVAÇÃO,
            "consulta": self.BOOST_CONSULTA,
            "edição": self.BOOST_EDIÇÃO,
        }
        return boosts.get(tipo, self.BOOST_REATIVAÇÃO)

    async def get_histórico_reativações(
        self,
        ilha_id: str,
        dias: int = 30,
    ) -> List[Dict[str, Any]]:
        """
        Obter histórico de reativações de uma ilha.

        Args:
            ilha_id: ID da ilha
            dias: Número de dias a considerar

        Returns:
            Lista de reativações
        """
        # Esta função precisaria de uma query específica no repository
        # Por agora, retornamos vazio
        return []
