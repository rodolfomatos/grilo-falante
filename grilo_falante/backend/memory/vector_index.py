"""
Vector Index — pgvector similarity search for claims

Provides:
- Embedding generation
- Vector similarity search
- Consensus search (multiple similar results)
"""

from typing import List, Optional
import httpx

from grilo_falante.config import settings


class VectorIndex:
    """
    Vector similarity index using pgvector.
    """

    def __init__(self, embedding_url: Optional[str] = None):
        self.embedding_url = embedding_url or "http://localhost:11434"
        self.dimension = 768

    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for text using Ollama."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.embedding_url}/api/embeddings",
                json={
                    "model": settings.ollama_model,
                    "prompt": text,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data.get("embedding", [])

    async def search(
        self,
        query_embedding: List[float],
        limit: int = 10,
        match_threshold: float = 0.5,
    ) -> List[dict]:
        """
        Search for similar claims using vector similarity.
        Returns list of claims with scores.
        """
        from grilo_falante.backend.db.repositories import ClaimRepository

        repo = ClaimRepository()
        return await repo.vector_search(query_embedding, limit, match_threshold)

    async def search_consensus(
        self,
        query_embedding: List[float],
        min_support: int = 2,
    ) -> List[dict]:
        """
        Search for claims that have consensus (multiple sources supporting same claim).
        """
        results = await self.search(query_embedding, limit=50)

        claim_groups = {}
        for r in results:
            key = r.get("claim_key", r.get("claim_text", ""))
            if key not in claim_groups:
                claim_groups[key] = []
            claim_groups[key].append(r)

        consensus_results = []
        for key, group in claim_groups.items():
            if len(group) >= min_support:
                avg_score = sum(g.get("score", 0) for g in group) / len(group)
                first = group[0].copy()
                first["score"] = avg_score
                first["support_count"] = len(group)
                consensus_results.append(first)

        consensus_results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return consensus_results[:10]

    async def add_claim_embedding(self, claim_id: int, text: str) -> None:
        """Add embedding for a claim."""
        embedding = await self.embed_text(text)
        from grilo_falante.backend.db.repositories import ClaimRepository

        repo = ClaimRepository()
        await repo.update_embedding(claim_id, embedding)
