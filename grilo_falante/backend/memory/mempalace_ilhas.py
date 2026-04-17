"""
MemPalace Island Integration — Sistema de Memória Insular

Este módulo integra o MemPalace (ChromaDB) com o sistema de Ilhas.

O MemPalace serve como índice de evocação rápido (fast recall),
enquanto o sistema de Ilhas fornece a ontologia e estrutura.

Conceito:
- MemPalace = índice de evocação (semelhanças, proximidade)
- Ilhas = centros de gravidade semânticos (agregados)
- O sistema de Ilhas decide QUANDO agregar
- O MemPalace ajuda a ENCONTRAR relações
"""

import logging
from typing import List, Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from app.ontology.ilhas import Ilha, Pedra

logger = logging.getLogger(__name__)

MEMPALACE_AVAILABLE = False
try:
    from mempalace.searcher import search_memories
    from mempalace.knowledge_graph import KnowledgeGraph

    MEMPALACE_AVAILABLE = True
except ImportError:
    logger.warning("MemPalace not available - island recall disabled")


WING_ILHAS = "wing_ilhas"
WING_PEDRAS = "wing_pedras"
WING_CLAIMS = "wing_claims"


class MemPalaceIlhas:
    """
    MemPalace integration for Memory Islands.

    Uses MemPalace wings to organize:
    - wing_ilhas: aggregated islands
    - wing_pedras: salient stones
    - wing_claims: claims within islands
    """

    def __init__(
        self,
        palace_path: Optional[str] = None,
    ):
        """
        Initialize MemPalace for Islands.

        Args:
            palace_path: Path to MemPalace data directory
        """
        self.palace_path = palace_path or "/home/rodolfo/.mempalace/palace"
        self._kg = None

    def _ensure_client(self) -> bool:
        """Lazy initialization."""
        if not MEMPALACE_AVAILABLE:
            return False

        if self._kg is None:
            try:
                self._kg = KnowledgeGraph(db_path=self.palace_path)
                logger.info(f"MemPalace connected: {self.palace_path}")
            except Exception as e:
                logger.warning(f"MemPalace connection failed: {e}")
                self._kg = None

        return self._kg is not None

    async def guardar_ilha(self, ilha: "Ilha") -> bool:
        """
        Guardar uma ilha no MemPalace.

        Args:
            ilha: Ilha object to store

        Returns:
            True if successful
        """
        if not self._ensure_client():
            return False

        try:
            self._kg.add_claim(
                claim_id=ilha.id,
                claim_text=ilha.descrição or ilha.nome,
                gmif_type="ILHA",
                metadata={
                    "wing": WING_ILHAS,
                    "nome": ilha.nome,
                    "estado": ilha.estado.value,
                    "score": ilha.score_ativação,
                    "membros_count": len(ilha.membros),
                },
            )

            for relação in ilha.relações:
                self._kg.add_triple(
                    entity1=ilha.id,
                    relation=f"REL_{relação.tipo.value}",
                    entity2=relação.ilha_id,
                )

            logger.debug(f"Guardou ilha {ilha.id} no MemPalace")
            return True

        except Exception as e:
            logger.warning(f"MemPalace guardar_ilha failed: {e}")
            return False

    async def guardar_pedra(self, pedra: "Pedra") -> bool:
        """
        Guardar uma pedra no MemPalace.

        Args:
            pedra: Pedra object to store

        Returns:
            True if successful
        """
        if not self._ensure_client():
            return False

        try:
            self._kg.add_claim(
                claim_id=pedra.id,
                claim_text=pedra.conteúdo_original[:200] if pedra.conteúdo_original else "",
                gmif_type="PEDRA",
                metadata={
                    "wing": WING_PEDRAS,
                    "tipo": pedra.tipo_interação.value,
                    "saliência": pedra.saliência.valor,
                    "estado": pedra.estado.value,
                },
            )
            logger.debug(f"Guardou pedra {pedra.id} no MemPalace")
            return True

        except Exception as e:
            logger.warning(f"MemPalace guardar_pedra failed: {e}")
            return False

    async def encontrar_ilhas_similares(
        self,
        query: str,
        limit: int = 5,
        threshold: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """
        Encontrar ilhas semanticamente similares a uma query.

        Args:
            query: Query text
            limit: Maximum results
            threshold: Minimum similarity score

        Returns:
            List of similar islands
        """
        if not self._ensure_client():
            return []

        try:
            results = search_memories(
                query,
                n_results=limit,
                palace_path=self.palace_path,
            )

            similares = []
            for r in results.get("results", []):
                if r.get("wing") == WING_ILHAS:
                    score = r.get("similarity", 0)
                    if score >= threshold:
                        similares.append(
                            {
                                "ilha_id": r.get("source_file", ""),
                                "nome": r.get("metadata", {}).get("nome", ""),
                                "score": score,
                                "estado": r.get("metadata", {}).get("estado", ""),
                            }
                        )

            return similares

        except Exception as e:
            logger.warning(f"MemPalace encontrar_ilhas_similares failed: {e}")
            return []

    async def encontrar_pedras_similares(
        self,
        query: str,
        limit: int = 10,
        threshold: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """
        Encontrar pedras semanticamente similares a uma query.

        Args:
            query: Query text
            limit: Maximum results
            threshold: Minimum similarity score

        Returns:
            List of similar stones
        """
        if not self._ensure_client():
            return []

        try:
            results = search_memories(
                query,
                n_results=limit,
                palace_path=self.palace_path,
            )

            similares = []
            for r in results.get("results", []):
                if r.get("wing") == WING_PEDRAS:
                    score = r.get("similarity", 0)
                    if score >= threshold:
                        similares.append(
                            {
                                "pedra_id": r.get("source_file", ""),
                                "conteúdo": r.get("text", "")[:100],
                                "score": score,
                                "saliência": r.get("metadata", {}).get("saliência", 0),
                            }
                        )

            return similares

        except Exception as e:
            logger.warning(f"MemPalace encontrar_pedras_similares failed: {e}")
            return []

    async def encontrar_agregados_relevantes(
        self,
        embedding: List[float],
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Encontrar ilhas/pedras relevantes para um embedding.

        Usa相似idade vectorial para encontrar relacionados.

        Args:
            embedding: Query embedding vector
            limit: Maximum results

        Returns:
            List of relevant aggregates
        """
        if not self._ensure_client():
            return []

        try:
            from mempalace.searcher import find_similar_vectors

            results = find_similar_vectors(
                embedding=embedding,
                n_results=limit,
                palace_path=self.palace_path,
            )

            relevantes = []
            for r in results.get("results", []):
                relevantes.append(
                    {
                        "id": r.get("id", ""),
                        "type": "ILHA" if r.get("type") == WING_ILHAS else "PEDRA",
                        "score": r.get("similarity", 0),
                    }
                )

            return relevantes

        except Exception as e:
            logger.warning(f"MemPalace encontrar_agregados_relevantes failed: {e}")
            return []

    async def adicionar_relação_ilha(
        self,
        ilha1_id: str,
        ilha2_id: str,
        tipo: str,
        força: float = 0.5,
    ) -> bool:
        """
        Adicionar relação entre duas ilhas.

        Args:
            ilha1_id: First island ID
            ilha2_id: Second island ID
            tipo: Relation type
            força: Relation strength (0-1)

        Returns:
            True if successful
        """
        if not self._ensure_client():
            return False

        try:
            self._kg.add_triple(
                entity1=ilha1_id,
                relation=f"REL_{tipo}",
                entity2=ilha2_id,
            )
            return True

        except Exception as e:
            logger.warning(f"MemPalace adicionar_relação_ilha failed: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get MemPalace statistics."""
        return {
            "available": MEMPALACE_AVAILABLE,
            "connected": self._kg is not None,
            "palace_path": self.palace_path,
        }
