"""
Gestor de Ilhas - Gestão de memória insular

Este módulo implementa a gestão de ilhas:
- Criar, atualizar, combinar ilhas
- Adicionar/remover membros
- Calcular estados e scores
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from app.ontology.ilhas import Ilha, Pedra, MembroIlha
    from app.ontology.estados import EstadoIlha

from app.ontology.ilhas import Ilha, MembroIlha, Saliencia
from app.ontology.estados import EstadoIlha
from grilo_falante.backend.db.ilhas_repository import IlhaRepository
from grilo_falante.backend.memory.mempalace_ilhas import MemPalaceIlhas

logger = logging.getLogger(__name__)


class GestorIlhas:
    """
    Gestor de Ilhas - interface para manipulação de ilhas.

    Encapsula a lógica de negócio para:
    - Criação e transformação de ilhas
    - Adição e remoção de membros
    - Combinação de ilhas
    - Gestão de estados
    """

    def __init__(
        self,
        repo: Optional[IlhaRepository] = None,
        mempalace: Optional[MemPalaceIlhas] = None,
    ):
        self.repo = repo or IlhaRepository()
        self.mempalace = mempalace or MemPalaceIlhas()

    async def criar_ilha_de_pedra(self, pedra: "Pedra") -> Ilha:
        """
        Criar uma nova ilha a partir de uma pedra.

        Args:
            pedra: Pedra que vai fundar a ilha

        Returns:
            Nova ilha criada
        """
        ilha = Ilha.criar_de_pedra(pedra)
        ilha.estado = EstadoIlha.EMBRIONARIA

        await self.repo.criar(ilha)
        await self.mempalace.guardar_ilha(ilha)

        logger.info(f"Criada ilha {ilha.id} a partir de pedra {pedra.id}")
        return ilha

    async def adicionar_membro(
        self,
        ilha_id: str,
        membro: MembroIlha,
    ) -> bool:
        """
        Adicionar um membro a uma ilha.

        Args:
            ilha_id: ID da ilha
            membro: Membro a adicionar

        Returns:
            True se adicionado com sucesso
        """
        ilha = await self.repo.obter(ilha_id)
        if not ilha:
            logger.warning(f"Ilha {ilha_id} não encontrada")
            return False

        if ilha.tem_membro(membro.member_id):
            logger.debug(f"Membro {membro.member_id} já existe em {ilha_id}")
            return True

        ilha.adicionar_membro(membro)
        await self.repo.adicionar_membro(ilha_id, membro)

        logger.debug(f"Adicionado membro {membro.member_id} a ilha {ilha_id}")
        return True

    async def remover_membro(
        self,
        ilha_id: str,
        member_id: str,
    ) -> bool:
        """
        Remover um membro de uma ilha.

        Args:
            ilha_id: ID da ilha
            member_id: ID do membro a remover

        Returns:
            True se removido com sucesso
        """
        ilha = await self.repo.obter(ilha_id)
        if not ilha:
            return False

        if ilha.remover_membro(member_id):
            await self.repo.atualizar(ilha)
            logger.debug(f"Removido membro {member_id} de ilha {ilha_id}")
            return True

        return False

    async def combinar_ilhas(
        self,
        ilha1_id: str,
        ilha2_id: str,
        força_relação: float = 0.8,
    ) -> Optional[Ilha]:
        """
        Combinar duas ilhas numa só.

        Args:
            ilha1_id: Primeira ilha (vai absorver a segunda)
            ilha2_id: Segunda ilha (vai ser absorvida)
            força_relação: Força da relação entre elas

        Returns:
            Ilha combinada ou None se erro
        """
        ilha1 = await self.repo.obter(ilha1_id)
        ilha2 = await self.repo.obter(ilha2_id)

        if not ilha1 or not ilha2:
            logger.warning(f"Uma das ilhas não foi encontrada: {ilha1_id}, {ilha2_id}")
            return None

        # Transferir membros
        for membro in ilha2.membros:
            if not ilha1.tem_membro(membro.member_id):
                ilha1.adicionar_membro(membro)

        # Adicionar relações
        from app.ontology.ilhas import RelacaoIlha
        from app.ontology.estados import TipoRelacao

        relação = RelacaoIlha(
            ilha_id=ilha2_id,
            tipo=TipoRelacao.AGREGADO_EM,
            força=força_relação,
        )
        ilha1.adicionar_relação(relação)

        # Atualizar scores
        ilha1.grau_consolidação = min(
            1.0,
            (ilha1.grau_consolidação + ilha2.grau_consolidação) / 2
        )
        ilha1.score_ativação = max(ilha1.score_ativação, ilha2.score_ativação)

        # Se a segunda tinha membros válidos, marcar como consolidada
        if len(ilha2.membros) >= 10:
            ilha1.estado = EstadoIlha.CONSOLIDADA

        # Guardar
        await self.repo.atualizar(ilha1)
        await self.mempalace.guardar_ilha(ilha1)

        # Eliminar a segunda (ou marcar como inativa)
        ilha2.estado = EstadoIlha.DORMINTE
        await self.repo.atualizar(ilha2)

        logger.info(f"Combinadas ilhas {ilha1_id} e {ilha2_id}")
        return ilha1

    async def obter_ilha(self, ilha_id: str) -> Optional[Ilha]:
        """Obter uma ilha pelo ID."""
        return await self.repo.obter(ilha_id)

    async def listar_ilhas(
        self,
        estado: Optional[str] = None,
        limit: int = 100,
    ) -> List[Ilha]:
        """Listar ilhas, opcionalmente filtradas por estado."""
        return await self.repo.listar(estado=estado, limit=limit)

    async def listar_ativas(
        self,
        threshold: float = 0.5,
    ) -> List[Ilha]:
        """Listar ilhas ativas acima do threshold."""
        return await self.repo.listar_ativas(threshold=threshold)

    async def actualizar_estado_ilha(
        self,
        ilha_id: str,
        novo_estado: "EstadoIlha",
    ) -> bool:
        """
        Atualizar o estado de uma ilha.

        Args:
            ilha_id: ID da ilha
            novo_estado: Novo estado

        Returns:
            True se atualizado
        """
        ilha = await self.repo.obter(ilha_id)
        if not ilha:
            return False

        ilha.estado = novo_estado
        await self.repo.atualizar(ilha)
        await self.mempalace.guardar_ilha(ilha)

        logger.info(f"Ilha {ilha_id} atualizada para estado {novo_estado.value}")
        return True

    async def adicionar_lacuna(
        self,
        ilha_id: str,
        lacuna: str,
    ) -> bool:
        """
        Adicionar uma lacuna identificada a uma ilha.

        Args:
            ilha_id: ID da ilha
            lacuna: Descrição da lacuna

        Returns:
            True se adicionada
        """
        ilha = await self.repo.obter(ilha_id)
        if not ilha:
            return False

        if lacuna not in ilha.lacunas_identificadas:
            ilha.lacunas_identificadas.append(lacuna)
            await self.repo.atualizar(ilha)

        return True

    async def get_resumo_sistema(self) -> Dict[str, Any]:
        """
        Obter resumo do estado do sistema de ilhas.

        Returns:
            Dict com estatísticas
        """
        todas = await self.repo.listar(limit=1000)

        activas = [i for i in todas if i.score_ativação >= 0.5]
        erodindo = [i for i in todas if 0.1 <= i.score_ativação < 0.5]
        dormintes = [i for i in todas if i.score_ativação < 0.1]

        return {
            "total_ilhas": len(todas),
            "activas": len(activas),
            "erodindo": len(erodindo),
            "dormintes": len(dormintes),
            "total_membros": sum(len(i.membros) for i in todas),
            "total_lacunas": sum(len(i.lacunas_identificadas) for i in todas),
        }
