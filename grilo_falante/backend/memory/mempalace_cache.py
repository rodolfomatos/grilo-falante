"""
MemPalace Cache — Fast semantic cache using MemPalace

MemPalace provides fast semantic search using ChromaDB.
This integration uses MemPalace as a first-pass cache layer,
with PostgreSQL + pgvector as the authoritative store.

Architecture:
    Query → MemPalace (fast) → PostgreSQL (authoritative)
                       ↓
              If cache miss or stale → Full retrieval
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

MEMPALACE_AVAILABLE = False
try:
    from mempalace.searcher import search_memories
    from mempalace.knowledge_graph import KnowledgeGraph
    MEMPALACE_AVAILABLE = True
except ImportError:
    logger.warning("MemPalace not available - semantic cache disabled")


class MemPalaceCache:
    """
    MemPalace-backed semantic cache for fast queries.

    Uses MemPalace (ChromaDB) for:
    - Fast first-pass semantic search
    - Query expansion
    - Context retrieval

    The authoritative store remains PostgreSQL + pgvector.
    """

    def __init__(
        self,
        palace_path: Optional[str] = None,
        collection_name: str = "grilo_cache",
        ttl_seconds: int = 3600,
    ):
        """
        Initialize MemPalace cache.

        Args:
            palace_path: Path to MemPalace data directory
            collection_name: Collection name for cached items
            ttl_seconds: Time-to-live for cache entries
        """
        self.palace_path = palace_path or "/home/rodolfo/.mempalace/knowledge_graph.sqlite3"
        self.collection_name = collection_name
        self.ttl_seconds = ttl_seconds
        self._client = None
        self._kg = None

    def _ensure_client(self):
        """Lazy initialization of MemPalace client."""
        if not MEMPALACE_AVAILABLE:
            return False

        if self._client is None:
            try:
                self._kg = KnowledgeGraph(db_path=self.palace_path)
                self._client = True
                logger.info(f"MemPalace connected: {self.palace_path}")
            except Exception as e:
                logger.warning(f"MemPalace connection failed: {e}")
                self._client = False
                self._kg = None

        return self._client is True

    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fast semantic search using MemPalace.

        Returns cached results if available, empty list if cache miss.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of cached claims with scores
        """
        if not self._ensure_client():
            return []

        try:
            raw_results = search_memories(
                query,
                n_results=limit,
                palace_path="/home/rodolfo/.mempalace/palace",
            )

            cached = []
            for r in raw_results.get("results", []):
                cached.append({
                    "claim_id": r.get("source_file", ""),
                    "claim_text": r.get("text", ""),
                    "gmif_level": "M4",
                    "score": r.get("similarity", 0.5),
                    "wing": r.get("wing", ""),
                    "room": r.get("room", ""),
                    "cached": True,
                    "source": "mempalace",
                })

            logger.info(f"MemPalace cache hit: {len(cached)} results for '{query[:50]}'")
            return cached

        except Exception as e:
            logger.warning(f"MemPalace search failed: {e}")
            return []

    async def store(
        self,
        claim_id: str,
        claim_text: str,
        gmif_level: str = "M4",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Store a claim in MemPalace cache.

        Args:
            claim_id: Unique claim identifier
            claim_text: Claim text content
            gmif_level: GMIF classification
            metadata: Additional metadata

        Returns:
            True if stored successfully
        """
        if not self._ensure_client():
            return False

        try:
            if self._kg is None:
                return False

            self._kg.add_claim(
                claim_id=claim_id,
                claim_text=claim_text,
                gmif_type=gmif_level,
                metadata=metadata or {},
            )

            logger.debug(f"Cached claim {claim_id} in MemPalace")
            return True

        except Exception as e:
            logger.warning(f"MemPalace store failed: {e}")
            return False

    async def store_batch(
        self,
        claims: List[Dict[str, Any]],
    ) -> int:
        """
        Store multiple claims in cache.

        Args:
            claims: List of claim dicts with claim_id, claim_text, gmif_level

        Returns:
            Number of successfully cached claims
        """
        if not self._ensure_client() or not claims:
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

        logger.info(f"MemPalace batch cache: {stored}/{len(claims)} claims")
        return stored

    async def invalidate(self, claim_id: str) -> bool:
        """
        Remove a claim from cache.

        Args:
            claim_id: Claim to remove

        Returns:
            True if removed successfully
        """
        if not self._ensure_client():
            return False

        try:
            if self._kg:
                self._kg.remove_claim(claim_id)
            return True
        except Exception as e:
            logger.warning(f"MemPalace invalidate failed: {e}")
            return False

    async def clear(self) -> bool:
        """
        Clear all cached claims.

        Returns:
            True if cleared successfully
        """
        if not self._ensure_client():
            return False

        try:
            if self._kg:
                self._kg.clear()
            logger.info("MemPalace cache cleared")
            return True
        except Exception as e:
            logger.warning(f"MemPalace clear failed: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dict with cache stats
        """
        return {
            "available": MEMPALACE_AVAILABLE,
            "connected": self._client is True,
            "palace_path": self.palace_path,
            "collection": self.collection_name,
        }


class HybridCacheRetriever:
    """
    Hybrid retrieval using MemPalace as first-pass cache.

    Flow:
    1. Query MemPalace (fast, ~10ms)
    2. If cache miss → Query PostgreSQL (authoritative)
    3. Store results in MemPalace for next time

    Scoring:
    - MemPalace results: semantic_score only
    - PostgreSQL results: semantic + epistemic (65/35)
    """

    MEMPALACE_WEIGHT = 0.3
    POSTGRES_WEIGHT = 0.7

    def __init__(
        self,
        mempalace: Optional[MemPalaceCache] = None,
        hybrid_retriever: Optional[Any] = None,
    ):
        """
        Initialize hybrid cache retriever.

        Args:
            mempalace: MemPalaceCache instance
            hybrid_retriever: HybridRetriever instance for authoritative queries
        """
        self.mempalace = mempalace or MemPalaceCache()
        self.hybrid_retriever = hybrid_retriever

    async def retrieve(
        self,
        query: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve claims using cache-first strategy.

        Args:
            query: User query
            limit: Maximum results

        Returns:
            List of claims with scores
        """
        mempalace_results = await self.mempalace.search(query, limit=limit)

        if mempalace_results and len(mempalace_results) >= limit:
            logger.info("MemPalace cache hit - returning cached results")
            return mempalace_results[:limit]

        if self.hybrid_retriever is None:
            return mempalace_results

        pg_results = await self.hybrid_retriever.retrieve(query, limit=limit)

        if pg_results and not mempalace_results:
            await self.mempalace.store_batch(pg_results)
            logger.info("PostgreSQL results cached in MemPalace")

        if mempalace_results and pg_results:
            merged = self._merge_results(mempalace_results, pg_results)
            await self.mempalace.store_batch(pg_results)
            return merged[:limit]

        return pg_results or mempalace_results

    def _merge_results(
        self,
        cache_results: List[Dict],
        pg_results: List[Dict],
    ) -> List[Dict[str, Any]]:
        """
        Merge cache and PostgreSQL results.

        PostgreSQL results take precedence, cache provides context.
        """
        seen_ids = set()
        merged = []

        for pg in pg_results:
            claim_id = pg.get("claim_id", pg.get("id", ""))
            if claim_id not in seen_ids:
                merged.append({
                    **pg,
                    "cached": False,
                    "source": "postgresql",
                })
                seen_ids.add(claim_id)

        for cache in cache_results:
            claim_id = cache.get("claim_id", cache.get("id", ""))
            if claim_id not in seen_ids:
                merged.append({
                    **cache,
                    "final_score": cache.get("score", 0) * self.MEMPALACE_WEIGHT,
                    "cached": True,
                    "source": "mempalace",
                })
                seen_ids.add(claim_id)

        merged.sort(key=lambda x: x.get("final_score", 0), reverse=True)
        return merged