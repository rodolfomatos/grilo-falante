"""
Acordar - Restauração de contexto para novo dia

Este módulo implementa o ciclo Acordar:
- Carregar estado persistente das ilhas
- Restaurar contexto das ilhas ativas
- Construir bundle de reentrada para tarefa
- Identificar lacunas
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.ontology.ilhas import Ilha, MembroIlha
from app.ontology.estados import EstadoIlha
from grilo_falante.backend.db.ilhas_repository import (
    IlhaRepository,
    PedraRepository,
)
from grilo_falante.backend.memory.mempalace_ilhas import MemPalaceIlhas

logger = logging.getLogger(__name__)


class ContextoRestaurado:
    """Contexto restaurado após acordar."""

    def __init__(
        self,
        session_id: str,
        ilhas_ativas: List[Ilha],
        ilhas_dormintes: List[Ilha],
        bundle: Optional[Dict[str, Any]] = None,
    ):
        self.session_id = session_id
        self.ilhas_ativas = ilhas_ativas
        self.ilhas_dormintes = ilhas_dormintes
        self.bundle = bundle
        self.data_acordar = datetime.now()

    def para_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "data_acordar": self.data_acordar.isoformat(),
            "ilhas_ativas_count": len(self.ilhas_ativas),
            "ilhas_dormintes_count": len(self.ilhas_dormintes),
            "bundle": self.bundle,
        }


class BundleReentrada:
    """
    Bundle de reentrada para uma tarefa.

    Reúne tudo o que é necessário para continuar o trabalho:
    - Tópicos relevantes
    - Perguntas operativas
    - Artefactos centrais
    - Claims associadas
    - Fontes relevantes
    - Conflitos e lacunas
    """

    def __init__(
        self,
        tarefa: str,
        ilhas_relacionadas: List[Ilha],
        claims: List[Dict[str, Any]],
        lacunas: List[str],
        conflitos: List[str],
    ):
        self.tarefa = tarefa
        self.ilhas_relacionadas = ilhas_relacionadas
        self.claims = claims
        self.lacunas = lacunas
        self.conflitos = conflitos

    def para_dict(self) -> Dict[str, Any]:
        return {
            "tarefa": self.tarefa,
            "ilhas": [
                {
                    "id": i.id,
                    "nome": i.nome,
                    "descrição": i.descrição,
                    "score": i.score_ativação,
                    "membros_count": len(i.membros),
                }
                for i in self.ilhas_relacionadas
            ],
            "claims_count": len(self.claims),
            "lacunas": self.lacunas,
            "conflitos": self.conflitos,
        }


async def acordar(
    session_id: str,
    tarefa: Optional[str] = None,
) -> ContextoRestaurado:
    """
    Função principal do ciclo Acordar.

    Args:
        session_id: ID da sessão
        tarefa: Tarefa opcional para construir bundle de reentrada

    Returns:
        Contexto restaurado com ilhas ativas
    """
    logger.info(f"Iniciando Acordar para sessão {session_id}, tarefa={tarefa}")

    ilha_repo = IlhaRepository()
    pedra_repo = PedraRepository()
    mempalace = MemPalaceIlhas()

    # Passo 1: Carregar estado persistente
    ilhas = await ilha_repo.listar(limit=100)

    # Passo 2: Restaurar contexto de ilhas ativas
    threshold_ativo = 0.5
    ilhas_ativas = [i for i in ilhas if i.score_ativação >= threshold_ativo]
    ilhas_dormintes = [i for i in ilhas if i.score_ativação < threshold_ativo]

    logger.info(f"Carregadas {len(ilhas_ativas)} ilhas ativas, {len(ilhas_dormintes)} dormintes")

    # Passo 3: Se há tarefa, construir bundle de reentrada
    bundle = None
    if tarefa:
        bundle = await _construir_bundle(
            tarefa=tarefa,
            ilhas=ilhas,
            mempalace=mempalace,
        )

    # Atualizar histórico de reativações
    for ilha in ilhas_ativas:
        from app.ontology.ilhas import HistóricoReativacao

        await ilha_repo.adicionar_reação(
            ilha.id,
            HistóricoReativacao(
                tipo="reativação",
                session_id=session_id,
            ),
        )

    return ContextoRestaurado(
        session_id=session_id,
        ilhas_ativas=ilhas_ativas,
        ilhas_dormintes=ilhas_dormintes,
        bundle=bundle.para_dict() if bundle else None,
    )


async def _construir_bundle(
    tarefa: str,
    ilhas: List[Ilha],
    mempalace: MemPalaceIlhas,
) -> BundleReentrada:
    """
    Construir bundle de reentrada para uma tarefa.

    Args:
        tarefa: Descrição da tarefa
        ilhas: Lista de ilhas disponíveis
        mempalace: MemPalace para busca

    Returns:
        Bundle de reentrada
    """
    # Buscar ilhas relacionadas no MemPalace
    similares = await mempalace.encontrar_ilhas_similares(
        query=tarefa,
        limit=5,
        threshold=0.5,
    )

    # Encontrar ilhas correspondentes
    ilhas_relacionadas = []
    for sim in similares:
        ilha_id = sim["ilha_id"]
        ilha = next((i for i in ilhas if i.id == ilha_id), None)
        if ilha:
            ilhas_relacionadas.append(ilha)

    # Se não encontrou pelo MemPalace, usar todas as ativas
    if not ilhas_relacionadas:
        ilhas_relacionadas = [i for i in ilhas if i.score_ativação > 0.3][:5]

    # Coletar claims das ilhas relacionadas
    claims = []
    lacunas = []
    conflitos = []

    for ilha in ilhas_relacionadas:
        for membro in ilha.membros:
            if membro.tipo == "claim":
                claims.append({
                    "id": membro.member_id,
                    "saliência": membro.saliência,
                    "ilha": ilha.nome,
                })

        lacunas.extend(ilha.lacunas_identificadas)

    # Remover duplicados
    lacunas = list(set(lacunas))
    conflitos = list(set(conflitos))

    return BundleReentrada(
        tarefa=tarefa,
        ilhas_relacionadas=ilhas_relacionadas,
        claims=claims[:10],  # Limitar a 10 claims
        lacunas=lacunas[:5],  # Limitar a 5 lacunas
        conflitos=conflitos,
    )


async def acordar_com_tarefa(
    session_id: str,
    tarefa: str,
) -> ContextoRestaurado:
    """
    Variante de acordar que requer uma tarefa.

    Args:
        session_id: ID da sessão
        tarefa: Tarefa a realizar

    Returns:
        Contexto restaurado com bundle de reentrada
    """
    return await acordar(session_id, tarefa=tarefa)
