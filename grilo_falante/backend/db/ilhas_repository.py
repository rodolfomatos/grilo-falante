"""
Repository for Memory Islands (Ilhas e Pedras)

Handles persistence of islands, stones, and related entities.
"""

import json
import hashlib
from datetime import datetime, date
from typing import List, Optional, Dict, Any

import asyncpg

from app.ontology.ilhas import (
    Ilha,
    Pedra,
    Saliencia,
    MembroIlha,
    RelacaoIlha,
    HistóricoReativacao,
)
from app.ontology.estados import EstadoIlha, EstadoPedra, TipoRelacao
from grilo_falante.backend.db.connection import acquire_connection


class IlhaRepository:
    """Repository for Island persistence."""

    async def criar(self, ilha: Ilha) -> bool:
        """Create a new island."""
        async with acquire_connection() as conn:
            await conn.execute(
                """
                INSERT INTO ilhas (ilha_key, nome, descrição, estado,
                                 grau_consolidação, score_ativação,
                                 claims_validadas, claims_pendentes,
                                 lacunas_identificadas)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (ilha_key) DO NOTHING
                """,
                ilha.id,
                ilha.nome,
                ilha.descrição,
                ilha.estado.value,
                ilha.grau_consolidação,
                ilha.score_ativação,
                ilha.claims_validadas,
                ilha.claims_pendentes,
                json.dumps(ilha.lacunas_identificadas),
            )
            return True

    async def obter(self, ilha_key: str) -> Optional[Ilha]:
        """Get an island by key."""
        async with acquire_connection() as conn:
            row = await conn.fetchrow("SELECT * FROM ilhas WHERE ilha_key = $1", ilha_key)
            if not row:
                return None
            return self._row_to_ilha(row)

    async def listar(
        self,
        estado: Optional[str] = None,
        limit: int = 100,
    ) -> List[Ilha]:
        """List islands, optionally filtered by state."""
        async with acquire_connection() as conn:
            if estado:
                rows = await conn.fetch(
                    """
                    SELECT * FROM ilhas
                    WHERE estado = $1
                    ORDER BY score_ativação DESC
                    LIMIT $2
                    """,
                    estado,
                    limit,
                )
            else:
                rows = await conn.fetch(
                    """
                    SELECT * FROM ilhas
                    ORDER BY score_ativação DESC
                    LIMIT $1
                    """,
                    limit,
                )
            return [self._row_to_ilha(row) for row in rows]

    async def listar_ativas(self, threshold: float = 0.5) -> List[Ilha]:
        """List active islands above threshold."""
        async with acquire_connection() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM ilhas
                WHERE score_ativação >= $1
                ORDER BY score_ativação DESC
                """,
                threshold,
            )
            return [self._row_to_ilha(row) for row in rows]

    async def atualizar(self, ilha: Ilha) -> bool:
        """Update an island."""
        async with acquire_connection() as conn:
            await conn.execute(
                """
                UPDATE ilhas SET
                    nome = $2,
                    descrição = $3,
                    estado = $4,
                    grau_consolidação = $5,
                    score_ativação = $6,
                    claims_validadas = $7,
                    claims_pendentes = $8,
                    lacunas_identificadas = $9,
                    updated_at = NOW()
                WHERE ilha_key = $1
                """,
                ilha.id,
                ilha.nome,
                ilha.descrição,
                ilha.estado.value,
                ilha.grau_consolidação,
                ilha.score_ativação,
                ilha.claims_validadas,
                ilha.claims_pendentes,
                json.dumps(ilha.lacunas_identificadas),
            )
            return True

    async def adicionar_membro(
        self,
        ilha_key: str,
        membro: MembroIlha,
    ) -> bool:
        """Add a member to an island."""
        async with acquire_connection() as conn:
            await conn.execute(
                """
                INSERT INTO ilha_membros
                    (ilha_key, member_id, member_type, saliência, data_inserção, inserido_por)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (ilha_key, member_id, member_type) DO NOTHING
                """,
                ilha_key,
                membro.member_id,
                membro.tipo,
                membro.saliência,
                membro.data_inserção,
                membro.inserido_por,
            )
            return True

    async def adicionar_reação(
        self,
        ilha_key: str,
        reação: HistóricoReativacao,
    ) -> bool:
        """Add a reaction to an island."""
        async with acquire_connection() as conn:
            await conn.execute(
                """
                INSERT INTO ilha_reações (ilha_key, tipo, session_id, data)
                VALUES ($1, $2, $3, $4)
                """,
                ilha_key,
                reação.tipo,
                reação.session_id,
                reação.data,
            )
            return True

    def _row_to_ilha(self, row: asyncpg.Record) -> Ilha:
        """Convert database row to Ilha object."""
        return Ilha(
            id=row["ilha_key"],
            nome=row["nome"],
            descrição=row["descrição"],
            estado=EstadoIlha(row["estado"]),
            grau_consolidação=row["grau_consolidação"],
            score_ativação=row["score_ativação"],
            claims_validadas=row["claims_validadas"],
            claims_pendentes=row["claims_pendentes"],
            lacunas_identificadas=json.loads(row["lacunas_identificadas"] or "[]"),
            data_criação=row["data_criação"],
        )


class PedraRepository:
    """Repository for Stone (Pedra) persistence."""

    async def criar(self, pedra: Pedra) -> bool:
        """Create a new stone."""
        content_hash = ""
        if pedra.conteúdo_original:
            content_hash = hashlib.md5(pedra.conteúdo_original.encode()).hexdigest()

        async with acquire_connection() as conn:
            await conn.execute(
                """
                INSERT INTO pedras (
                    pedra_key, tipo_interação,
                    saliência_valor, saliência_frequência,
                    saliência_intensidade, saliência_novidade, saliência_relevância,
                    impacto_criou_ilha, ilha_criada_key,
                    estado, conteúdo_original, conteúdo_hash, embedding
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                ON CONFLICT (pedra_key) DO NOTHING
                """,
                pedra.id,
                pedra.tipo_interação.value,
                pedra.saliência.valor,
                pedra.saliência.frequência,
                pedra.saliência.intensidade,
                pedra.saliência.novidade,
                pedra.saliência.relevância,
                pedra.impacto_criou_ilha,
                pedra.ilha_criada,
                pedra.estado.value,
                pedra.conteúdo_original,
                content_hash,
                json.dumps(pedra.embedding) if pedra.embedding else None,
            )
            return True

    async def obter(self, pedra_key: str) -> Optional[Pedra]:
        """Get a stone by key."""
        async with acquire_connection() as conn:
            row = await conn.fetchrow("SELECT * FROM pedras WHERE pedra_key = $1", pedra_key)
            if not row:
                return None
            return self._row_to_pedra(row)

    async def listar(
        self,
        estado: Optional[str] = None,
        limit: int = 100,
    ) -> List[Pedra]:
        """List stones, optionally filtered by state."""
        async with acquire_connection() as conn:
            if estado:
                rows = await conn.fetch(
                    """
                    SELECT * FROM pedras
                    WHERE estado = $1
                    ORDER BY saliência_valor DESC
                    LIMIT $2
                    """,
                    estado,
                    limit,
                )
            else:
                rows = await conn.fetch(
                    """
                    SELECT * FROM pedras
                    ORDER BY saliência_valor DESC
                    LIMIT $1
                    """,
                    limit,
                )
            return [self._row_to_pedra(row) for row in rows]

    async def listar_pendentes(self, limit: int = 100) -> List[Pedra]:
        """List stones waiting to be aggregated."""
        return await self.listar(estado=EstadoPedra.EM_ESPERA.value, limit=limit)

    async def atualizar(self, pedra: Pedra) -> bool:
        """Update a stone."""
        async with acquire_connection() as conn:
            await conn.execute(
                """
                UPDATE pedras SET
                    tipo_interação = $2,
                    saliência_valor = $3,
                    saliência_frequência = $4,
                    saliência_intensidade = $5,
                    saliência_novidade = $6,
                    saliência_relevância = $7,
                    impacto_criou_ilha = $8,
                    ilha_criada_key = $9,
                    estado = $10,
                    última_reativação = $11,
                    contagem_reações = $12
                WHERE pedra_key = $1
                """,
                pedra.id,
                pedra.tipo_interação.value,
                pedra.saliência.valor,
                pedra.saliência.frequência,
                pedra.saliência.intensidade,
                pedra.saliência.novidade,
                pedra.saliência.relevância,
                pedra.impacto_criou_ilha,
                pedra.ilha_criada,
                pedra.estado.value,
                pedra.última_reativação,
                pedra.contagem_reações,
            )
            return True

    def _row_to_pedra(self, row: asyncpg.Record) -> Pedra:
        """Convert database row to Pedra object."""
        from app.ontology.estados import TipoInteracao

        saliência = Saliencia(
            valor=row["saliência_valor"],
            frequência=row["saliência_frequência"],
            intensidade=row["saliência_intensidade"],
            novidade=row["saliência_novidade"],
            relevância=row["saliência_relevância"],
        )

        embedding = None
        if row["embedding"]:
            try:
                embedding = json.loads(row["embedding"])
            except json.JSONDecodeError:
                pass

        return Pedra(
            id=row["pedra_key"],
            tipo_interação=TipoInteracao(row["tipo_interação"]),
            saliência=saliência,
            impacto_criou_ilha=row["impacto_criou_ilha"],
            ilha_criada=row["ilha_criada_key"],
            estado=EstadoPedra(row["estado"]),
            conteúdo_original=row["conteúdo_original"],
            embedding=embedding,
            data_criação=row["data_criação"],
            última_reativação=row["última_reativação"],
            contagem_reações=row["contagem_reações"],
        )


class LedgerRepository:
    """Repository for chronological ledger."""

    async def registar_dia(
        self,
        data: date,
        session_id: str,
        pedras_criadas: int = 0,
        ilhas_criadas: int = 0,
        ilhas_actualizadas: int = 0,
    ) -> bool:
        """Register a day's activity."""
        async with acquire_connection() as conn:
            await conn.execute(
                """
                INSERT INTO ledger_cronológico
                    (data, session_id, pedras_criadas, ilhas_criadas, ilhas_actualizadas)
                VALUES ($1, $2, $3, $4, $5)
                """,
                data,
                session_id,
                pedras_criadas,
                ilhas_criadas,
                ilhas_actualizadas,
            )
            return True

    async def marcar_dormir(
        self,
        data: date,
        session_id: str,
        relatório: str,
    ) -> bool:
        """Mark sleep cycle as executed for a day."""
        async with acquire_connection() as conn:
            await conn.execute(
                """
                UPDATE ledger_cronológico SET
                    ciclo_dormir_executado = TRUE,
                    relatório_sono = $3
                WHERE data = $1 AND session_id = $2
                """,
                data,
                session_id,
                relatório,
            )
            return True

    async def obter_resumo_dia(
        self,
        data: date,
    ) -> Optional[Dict[str, Any]]:
        """Get summary for a day."""
        async with acquire_connection() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM ledger_cronológico
                WHERE data = $1
                """,
                data,
            )
            if not rows:
                return None

            total_pedras = sum(r["pedras_criadas"] for r in rows)
            total_ilhas = sum(r["ilhas_criadas"] for r in rows)

            return {
                "data": data,
                "total_pedras": total_pedras,
                "total_ilhas": total_ilhas,
                "entradas": len(rows),
            }
