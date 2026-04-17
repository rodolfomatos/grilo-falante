"""
AutoMem Adapter — Optional recall layer using AutoMem

This adapter integrates AutoMem (FalkorDB + Qdrant) as an optional
first-pass cache layer, without replacing existing systems.

Architecture:
    Query → AutoMem (optional) → MemPalace → PostgreSQL (authoritative)
                       ↓
              If not enabled or miss → fallback to MemPalace

Usage:
    Set AUTOMEM_ENABLED=true in environment to enable.
    Default: disabled (backward compatible)
"""

import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

AUTOMEM_SDK_AVAILABLE = False
try:
    from automem import AutoMem
    from automem.types import Memory, Relation

    AUTOMEM_SDK_AVAILABLE = True
except ImportError:
    logger.warning("AutoMem SDK not available - install with: pip install automem")


@dataclass
class RecallResult:
    """Result from AutoMem recall."""
    memory_id: str
    text: str
    score: float
    gmif_level: str = "M4"
    metadata: Dict[str, Any] = None


class AutoMemAdapter:
    """
    Adapter for AutoMem as optional recall layer.

    Interface compatible with MemPalaceCache for easy integration:
    - search(query, limit) -> List[RecallResult]
    - store(claim_id, claim_text, gmif_level, metadata) -> bool
    - store_batch(claims) -> int
    - invalidate(claim_id) -> bool
    - bridge_discovery() -> List[str]
    - enrich() -> Dict

    When AUTOMEM_ENABLED=False (default), all methods return empty/false
    for seamless fallback.
    """

    def __init__(
        self,
        enabled: bool = False,
        falkordb_url: str = "http://localhost:8001",
        qdrant_url: str = "http://localhost:6333",
        collection: str = "grilo_falante",
    ):
        """
        Initialize AutoMem adapter.

        Args:
            enabled: Whether AutoMem is enabled (default: False)
            falkordb_url: FalkorDB connection URL
            qdrant_url: Qdrant connection URL
            collection: Collection name for memories
        """
        self.enabled = enabled and AUTOMEM_SDK_AVAILABLE
        self.falkordb_url = falkordb_url
        self.qdrant_url = qdrant_url
        self.collection = collection
        self._client = None

    @property
    def is_available(self) -> bool:
        """Check if AutoMem is available and enabled."""
        return self.enabled

    def _ensure_client(self) -> bool:
        """Lazy initialization of AutoMem client."""
        if not self.enabled:
            return False

        if self._client is None and AUTOMEM_SDK_AVAILABLE:
            try:
                self._client = AutoMem(
                    falkordb_url=self.falkordb_url,
                    qdrant_url=self.qdrant_url,
                )
                logger.info(f"AutoMem connected: FalkorDB={self.falkordb_url}, Qdrant={self.qdrant_url}")
            except Exception as e:
                logger.warning(f"AutoMem connection failed: {e}")
                self._client = False

        return self._client is not False

    async def search(
        self,
        query: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search memories using AutoMem's 9-component scoring.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of memory results with scores (empty if disabled)
        """
        if not self.enabled:
            logger.debug("AutoMem disabled - returning empty results")
            return []

        if not self._ensure_client():
            logger.warning("AutoMem unavailable - falling back")
            return []

        try:
            memories = self._client.recall(
                query=query,
                n_results=limit,
            )

            results = []
            for mem in memories:
                results.append({
                    "memory_id": mem.id,
                    "claim_text": mem.content,
                    "score": mem.importance,
                    "gmif_level": "M4",
                    "metadata": {
                        "created_at": mem.created_at,
                        "tags": mem.tags,
                        "relations": getattr(mem, 'relations', []),
                    },
                    "source": "automem",
                    "cached": True,
                })

            logger.info(f"AutoMem recall: {len(results)} results for '{query[:50]}'")
            return results

        except Exception as e:
            logger.warning(f"AutoMem recall failed: {e}")
            return []

    async def store(
        self,
        claim_id: str,
        claim_text: str,
        gmif_level: str = "M4",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Store a memory in AutoMem.

        Args:
            claim_id: Unique claim identifier
            claim_text: Claim text content
            gmif_level: GMIF classification
            metadata: Additional metadata

        Returns:
            True if stored successfully
        """
        if not self.enabled:
            return False

        if not self._ensure_client():
            return False

        try:
            memory = Memory(
                id=claim_id,
                content=claim_text,
                importance=0.5,
                tags=metadata.get("tags", []) if metadata else [],
                metadata=metadata or {},
            )

            self._client.store(memory)
            logger.debug(f"AutoMem stored: {claim_id}")
            return True

        except Exception as e:
            logger.warning(f"AutoMem store failed: {e}")
            return False

    async def store_batch(
        self,
        claims: List[Dict[str, Any]],
    ) -> int:
        """
        Store multiple memories in batch.

        Args:
            claims: List of claim dicts

        Returns:
            Number of successfully stored
        """
        if not self.enabled or not claims:
            return 0

        stored = 0
        for claim in claims:
            if await self.store(
                claim_id=claim.get("claim_id", claim.get("id", "")),
                claim_text=claim.get("claim_text", ""),
                gmif_level=claim.get("gmif_level", "M4"),
                metadata=claim,
            ):
                stored += 1

        logger.info(f"AutoMem batch store: {stored}/{len(claims)}")
        return stored

    async def invalidate(self, claim_id: str) -> bool:
        """
        Remove a memory from AutoMem.

        Args:
            claim_id: Memory to remove

        Returns:
            True if removed successfully
        """
        if not self.enabled:
            return False

        if not self._ensure_client():
            return False

        try:
            self._client.forget(claim_id)
            logger.debug(f"AutoMem invalidated: {claim_id}")
            return True

        except Exception as e:
            logger.warning(f"AutoMem invalidate failed: {e}")
            return False

    async def bridge_discovery(
        self,
        start_memory_id: str,
        max_hops: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Discover connections via bridge nodes (multi-hop).

        AutoMem's unique feature: find indirect connections
        through intermediate nodes.

        Args:
            start_memory_id: Starting memory ID
            max_hops: Maximum hops to traverse

        Returns:
            List of discovered memory connections
        """
        if not self.enabled:
            return []

        if not self._ensure_client():
            return []

        try:
            bridges = self._client.discover_bridges(
                start_id=start_memory_id,
                max_hops=max_hops,
            )

            results = []
            for bridge in bridges:
                results.append({
                    "memory_id": bridge.id,
                    "path": bridge.path,
                    "score": bridge.strength,
                })

            logger.info(f"AutoMem bridge discovery: {len(results)} connections from {start_memory_id}")
            return results

        except Exception as e:
            logger.warning(f"AutoMem bridge discovery failed: {e}")
            return []

    async def enrich(
        self,
        memory_id: str,
    ) -> Dict[str, Any]:
        """
        Enrich a memory with auto-extracted entities.

        Args:
            memory_id: Memory to enrich

        Returns:
            Enriched metadata
        """
        if not self.enabled:
            return {}

        if not self._ensure_client():
            return {}

        try:
            enriched = self._client.enrich(memory_id)
            return {
                "entities": enriched.get("entities", []),
                "summary": enriched.get("summary", ""),
                "tags": enriched.get("tags", []),
            }

        except Exception as e:
            logger.warning(f"AutoMem enrich failed: {e}")
            return {}

    async def consolidate(
        self,
    ) -> Dict[str, Any]:
        """
        Run consolidation cycle (decay, cluster, forget).

        Returns:
            Consolidation report
        """
        if not self.enabled:
            return {}

        if not self._ensure_client():
            return {}

        try:
            result = self._client.consolidate()
            return {
                "decayed": result.get("decayed", 0),
                "clustered": result.get("clustered", 0),
                "forgotten": result.get("forgotten", 0),
            }

        except Exception as e:
            logger.warning(f"AutoMem consolidate failed: {e}")
            return {}


class DualCacheRetriever:
    """
    Dual-layer cache: AutoMem + MemPalace fallback.

    Query flow:
        1. AutoMem (if enabled) → 2. MemPalace (fallback) → 3. PostgreSQL

    Storage flow (dual_write):
        1. AutoMem (if enabled AND dual_write) → 2. MemPalace
    """

    def __init__(
        self,
        automem: Optional[AutoMemAdapter] = None,
        mempalace: Optional[Any] = None,
        dual_write: bool = False,
    ):
        """
        Initialize dual cache retriever.

        Args:
            automem: AutoMem adapter instance
            mempalace: MemPalace cache instance
            dual_write: If True, store in both systems
        """
        self.automem = automem or AutoMemAdapter(enabled=False)
        self.mempalace = mempalace
        self.dual_write = dual_write

    async def search(
        self,
        query: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search with dual-layer fallback.

        AutoMem is tried first (if enabled), then MemPalace.
        """
        # Layer 1: AutoMem
        if self.automem.is_available:
            results = await self.automem.search(query, limit)
            if results:
                logger.info(f"DualCache: AutoMem hit ({len(results)} results)")
                return results

        # Layer 2: MemPalace fallback
        if self.mempalace:
            try:
                results = await self.mempalace.search(query, limit)
                if results:
                    logger.info(f"DualCache: MemPalace hit ({len(results)} results)")
                    return results
            except Exception as e:
                logger.warning(f"DualCache MemPalace fallback failed: {e}")

        logger.info(f"DualCache: cache miss for '{query[:30]}'")
        return []

    async def store(
        self,
        claim_id: str,
        claim_text: str,
        gmif_level: str = "M4",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Store in both caches (dual-write mode).
        """
        stored_automem = False
        stored_mempalace = False

        # AutoMem storage (if enabled)
        if self.automem.is_available:
            stored_automem = await self.automem.store(
                claim_id, claim_text, gmif_level, metadata
            )

        # MemPalace storage (always)
        if self.mempalace:
            try:
                stored_mempalace = await self.mempalace.store(
                    claim_id, claim_text, gmif_level, metadata
                )
            except Exception as e:
                logger.warning(f"DualCache MemPalace store failed: {e}")

        # If dual_write disabled, prefer MemPalace
        if not self.dual_write:
            return stored_mempalace

        return stored_automem or stored_mempalace

    async def store_batch(
        self,
        claims: List[Dict[str, Any]],
    ) -> int:
        """
        Store batch in both caches.
        """
        stored = 0
        for claim in claims:
            if await self.store(
                claim_id=claim.get("claim_id", claim.get("id", "")),
                claim_text=claim.get("claim_text", ""),
                gmif_level=claim.get("gmif_level", "M4"),
                metadata=claim,
            ):
                stored += 1

        logger.info(f"DualCache batch store: {stored}/{len(claims)}")
        return stored