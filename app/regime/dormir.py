"""
ProcessadorBatch - Processamento batch para o ciclo Ir Dormir

Este módulo implementa a sanitização de tudo o que se passou durante o "dia":
- Agregação em torno de centros de gravidade (pedras/ilhas)
- Identificação de saliências
- Atualização de estados
- Geração de relatório de sono
"""

import logging
from datetime import datetime, date
from typing import List, Dict, Any, Optional

from app.ontology.ilhas import Ilha, Pedra, Saliencia, MembroIlha
from app.ontology.estados import EstadoIlha, EstadoPedra, TipoInteracao
from grilo_falante.backend.db.ilhas_repository import (
    IlhaRepository,
    PedraRepository,
    LedgerRepository,
)
from grilo_falante.backend.memory.mempalace_ilhas import MemPalaceIlhas

logger = logging.getLogger(__name__)


class ProcessadorBatch:
    """
    Processador batch para o ciclo Ir Dormir.

    Executa os passos 1-8 do IR_DORMIR conforme especificado:
    1. Coletar interações desde último acordar
    2. Identificar pedras (saliências)
    3. Avaliar transformação em ilhas
    4. Agregar em torno de centros de gravidade
    5. Atualizar estado das ilhas existentes
    6. Consolidar memória
    7. Guardar em memória persistente
    8. Gerar relatório de sono
    """

    def __init__(
        self,
        ilha_repo: Optional[IlhaRepository] = None,
        pedra_repo: Optional[PedraRepository] = None,
        ledger_repo: Optional[LedgerRepository] = None,
        mempalace: Optional[MemPalaceIlhas] = None,
    ):
        self.ilha_repo = ilha_repo or IlhaRepository()
        self.pedra_repo = pedra_repo or PedraRepository()
        self.ledger_repo = ledger_repo or LedgerRepository()
        self.mempalace = mempalace or MemPalaceIlhas()

    async def executar(
        self,
        session_id: str,
        interações: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Executar o ciclo completo de Ir Dormir.

        Args:
            session_id: ID da sessão atual
            interações: Lista de interações desde o último acordar

        Returns:
            Relatório do ciclo de sono
        """
        relatório = {
            "session_id": session_id,
            "data": datetime.now().isoformat(),
            "passos_executados": [],
            "pedras_criadas": 0,
            "ilhas_criadas": 0,
            "ilhas_actualizadas": 0,
            "agregações_feitas": 0,
            "lacunas_identificadas": [],
            "sucesso": True,
            "erros": [],
        }

        try:
            logger.info(f"Iniciando Ir Dormir para sessão {session_id}")

            # Passo 1: Coletar interações (já recebido)
            relatório["passos_executados"].append("COLETAR")
            relatório["interações_recebidas"] = len(interações)

            # Passo 2: Identificar pedras
            pedras = await self._identificar_pedras(interações)
            relatório["pedras_criadas"] = len(pedras)
            relatório["passos_executados"].append("IDENTIFICAR_PEDRAS")

            for pedra in pedras:
                await self.pedra_repo.criar(pedra)
                await self.mempalace.guardar_pedra(pedra)

            # Passo 3: Avaliar transformação em ilhas
            novas_ilhas = await self._avaliar_transição_pedras(pedras)
            relatório["ilhas_criadas"] = len(novas_ilhas)
            relatório["passos_executados"].append("AVALIAR_TRANSFORMAÇÃO")

            for ilha in novas_ilhas:
                await self.ilha_repo.criar(ilha)
                await self.mempalace.guardar_ilha(ilha)

            # Passo 4: Agregar em torno de centros de gravidade
            agregações = await self._agregar_em_ilhas(pedras, novas_ilhas)
            relatório["agregações_feitas"] = agregações
            relatório["passos_executados"].append("AGREGAR")

            # Passo 5: Atualizar estado das ilhas existentes
            actualizadas = await self._actualizar_ilhas_existentes()
            relatório["ilhas_actualizadas"] = actualizadas
            relatório["passos_executados"].append("ACTUALIZAR_ILHAS")

            # Passo 6: Consolidar memória
            relatório["passos_executados"].append("CONSOLIDAR")

            # Passo 7: Guardar em memória persistente
            relatório["passos_executados"].append("GUARDAR")

            # Passo 8: Gerar relatório de sono
            await self._gerar_relatório_sono(
                session_id=session_id,
                relatório=relatório,
            )
            relatório["passos_executados"].append("RELATÓRIO")

            logger.info(
                f"Ir Dormir completo: {len(pedras)} pedras, "
                f"{len(novas_ilhas)} ilhas, {agregações} agregações"
            )

        except Exception as e:
            logger.error(f"Erro no ciclo Ir Dormir: {e}")
            relatório["sucesso"] = False
            relatório["erros"].append(str(e))

        return relatório

    async def _identificar_pedras(
        self,
        interações: List[Dict[str, Any]],
    ) -> List[Pedra]:
        """
        Passo 2: Identificar pedras (saliências).

        Uma interação torna-se pedra se tiver saliência suficiente.
        """
        pedras = []

        for interação in interações:
            saliência = self._calcular_saliência_interação(interação)

            # Threshold configurável
            if saliência.valor < 0.3:
                continue

            pedra = Pedra(
                tipo_interação=TipoInteracao(interação.get("tipo", "MENSAGEM")),
                saliência=saliência,
                conteúdo_original=interação.get("conteúdo", ""),
            )

            pedras.append(pedra)

        logger.debug(f"Identificadas {len(pedras)} pedras de {len(interações)} interações")
        return pedras

    def _calcular_saliência_interação(
        self,
        interação: Dict[str, Any],
    ) -> Saliencia:
        """
        Calcular saliência de uma interação.

        Componentes:
        - Frequência: quantas vezes surgiu
        - Intensidade: reações/engagement que gerou
        - Novidade: quão diferente é do que já existia
        - Relevância: conexão com ilhas existentes
        """
        frequência = min(1.0, interação.get("frequência", 0.5))
        intensidade = min(1.0, interação.get("intensidade", 0.3))
        novidade = min(1.0, interação.get("novidade", 0.5))
        relevância = min(1.0, interação.get("relevância", 0.4))

        return Saliencia.calcular(
            frequência=frequência,
            intensidade=intensidade,
            novidade=novidade,
            relevância=relevância,
        )

    async def _avaliar_transição_pedras(
        self,
        pedras: List[Pedra],
    ) -> List[Ilha]:
        """
        Passo 3: Avaliar se pedras devem transformar-se em ilhas.

        Condições para Pedra → Ilha:
        - saliência > 0.8 E
        - contagem_reações > 5 OU impacto_criou_ilha
        """
        novas_ilhas = []

        for pedra in pedras:
            if self._deve_transformar_em_ilha(pedra):
                ilha = pedra.transformar_em_ilha()
                novas_ilhas.append(ilha)
                logger.info(f"Pedra {pedra.id} transformou-se em Ilha {ilha.id}")

        return novas_ilhas

    def _deve_transformar_em_ilha(self, pedra: Pedra) -> bool:
        """Determinar se uma pedra deve criar uma nova ilha."""
        # Threshold alto de saliência
        if pedra.saliência.valor < 0.8:
            return False

        # Muitas reações OU impacto
        if pedra.contagem_reações > 5 or pedra.impacto_criou_ilha:
            return True

        return False

    async def _agregar_em_ilhas(
        self,
        pedras: List[Pedra],
        novas_ilhas: List[Ilha],
    ) -> int:
        """
        Passo 4: Agregar pedras em torno de centros de gravidade.

        Usa MemPalace para encontrar ilhas similares.
        """
        agregações = 0
        todas_ilhas = await self.ilha_repo.listar(limit=100)
        todas_ilhas.extend(novas_ilhas)

        for pedra in pedras:
            if pedra.está_agregada() or pedra.está_transformada():
                continue

            # Buscar ilhas similares no MemPalace
            similares = await self.mempalace.encontrar_ilhas_similares(
                query=pedra.conteúdo_original or "",
                limit=3,
                threshold=0.7,
            )

            if similares:
                # Agregar à ilha mais similar
                melhor = similares[0]
                ilha_id = melhor["ilha_id"]

                # Encontrar a ilha
                ilha = next(
                    (i for i in todas_ilhas if i.id == ilha_id),
                    None,
                )

                if ilha:
                    membro = MembroIlha(
                        member_id=pedra.id,
                        tipo=pedra.tipo_interação.value,
                        saliência=pedra.saliência.valor,
                        inserido_por="processador_batch",
                    )
                    ilha.adicionar_membro(membro)
                    pedra.agregar_a_ilha(ilha_id)

                    await self.ilha_repo.adicionar_membro(ilha_id, membro)
                    agregações += 1

        return agregações

    async def _actualizar_ilhas_existentes(self) -> int:
        """
        Passo 5: Atualizar estado das ilhas existentes.

        Aplica decay ao score e atualiza estados (ERODENDO, DORMINTE).
        """
        ilhas = await self.ilha_repo.listar(limit=100)
        actualizadas = 0

        for ilha in ilhas:
            # Aplicar decay
            ilha.aplicar_decay(factor=0.95)

            # Atualizar estado baseado no score
            if ilha.score_ativação < 0.1:
                if ilha.estado != EstadoIlha.DORMINTE:
                    ilha.estado = EstadoIlha.ERODENDO
                    actualizadas += 1
            elif ilha.score_ativação < 0.01:
                if ilha.estado != EstadoIlha.DORMINTE:
                    ilha.estado = EstadoIlha.DORMINTE
                    actualizadas += 1

            # Guardar
            await self.ilha_repo.atualizar(ilha)
            await self.mempalace.guardar_ilha(ilha)

        return actualizadas

    async def _gerar_relatório_sono(
        self,
        session_id: str,
        relatório: Dict[str, Any],
    ) -> None:
        """Passo 8: Gerar e guardar relatório de sono."""
        data_hoje = date.today()

        await self.ledger_repo.registar_dia(
            data=data_hoje,
            session_id=session_id,
            pedras_criadas=relatório.get("pedras_criadas", 0),
            ilhas_criadas=relatório.get("ilhas_criadas", 0),
            ilhas_actualizadas=relatório.get("ilhas_actualizadas", 0),
        )

        await self.ledger_repo.marcar_dormir(
            data=data_hoje,
            session_id=session_id,
            relatório=str(relatório),
        )


async def ir_dormir(
    session_id: str,
    interações: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Função principal do ciclo Ir Dormir.

    Args:
        session_id: ID da sessão
        interações: Lista de interações desde último acordar

    Returns:
        Relatório do ciclo de sono
    """
    processador = ProcessadorBatch()
    return await processador.executar(session_id, interações)
