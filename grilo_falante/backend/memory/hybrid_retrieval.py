"""
Hybrid Retrieval — Combines vector similarity with epistemic scoring

Scoring formula:
    final_score = 0.65 * semantic_score + 0.35 * epistemic_score

This provides:
- 65% weight to semantic relevance (vector similarity)
- 35% weight to epistemic quality (trustworthiness)
"""

from typing import List, Optional

from grilo_falante.backend.memory.vector_index import VectorIndex
from grilo_falante.backend.memory.knowledge_graph import KnowledgeGraphStore


class HybridRetriever:
    """
    Hybrid retrieval combining semantic and epistemic scoring.
    """

    SEMANTIC_WEIGHT = 0.65
    EPISTEMIC_WEIGHT = 0.35
    DEFAULT_LIMIT = 10
    MIN_SCORE_THRESHOLD = 0.05

    def __init__(
        self,
        vector_index: Optional[VectorIndex] = None,
        knowledge_graph: Optional[KnowledgeGraphStore] = None,
    ):
        self.vector_index = vector_index or VectorIndex()
        self.knowledge_graph = knowledge_graph or KnowledgeGraphStore()

    async def retrieve(
        self,
        query: str,
        limit: int = DEFAULT_LIMIT,
        require_epistemic: bool = False,
    ) -> List[dict]:
        """
        Retrieve claims for a query using hybrid scoring.

        Args:
            query: User query string
            limit: Maximum number of results
            require_epistemic: If True, filter out claims with very low epistemic score

        Returns:
            List of claims with combined scores
        """
        query_embedding = await self.vector_index.embed_text(query)

        vector_results = await self.vector_index.search(
            query_embedding,
            limit=limit * 3,
        )

        if not vector_results:
            return []

        combined_results = await self._combine_with_epistemic(vector_results)

        if require_epistemic:
            combined_results = [r for r in combined_results if r.get("epistemic_score", 0) > 0.2]

        combined_results.sort(key=lambda x: x.get("final_score", 0), reverse=True)

        return combined_results[:limit]

    async def retrieve_with_consensus(
        self,
        query: str,
        min_support: int = 2,
    ) -> List[dict]:
        """
        Retrieve claims that have consensus (multiple sources supporting same claim).
        """
        query_embedding = await self.vector_index.embed_text(query)

        consensus_results = await self.vector_index.search_consensus(
            query_embedding,
            min_support=min_support,
        )

        if not consensus_results:
            return []

        combined_results = await self._combine_with_epistemic(consensus_results)

        combined_results.sort(key=lambda x: x.get("final_score", 0), reverse=True)

        return combined_results

    async def _combine_with_epistemic(self, vector_results: List[dict]) -> List[dict]:
        """Add epistemic scores to vector results."""
        for result in vector_results:
            claim_id = result.get("id") or result.get("claim_id")

            if claim_id:
                epistemic_score = await self.knowledge_graph.get_epistemic_score(claim_id)
            else:
                epistemic_score = 0.5

            semantic_score = result.get("score", 0)

            final_score = (
                self.SEMANTIC_WEIGHT * semantic_score + self.EPISTEMIC_WEIGHT * epistemic_score
            )

            result["final_score"] = round(final_score, 4)
            result["epistemic_score"] = round(epistemic_score, 4)
            result["semantic_score"] = round(semantic_score, 4)

        return [r for r in vector_results if r.get("semantic_score", 0) > self.MIN_SCORE_THRESHOLD]

    async def expand_query(self, query: str, max_terms: int = 5) -> List[str]:
        """
        Expand query with related terms from the knowledge graph.
        """
        query_embedding = await self.vector_index.embed_text(query)

        results = await self.vector_index.search(query_embedding, limit=20)

        terms = [query]
        for r in results[:max_terms]:
            if r.get("claim_text"):
                terms.append(r["claim_text"][:100])

        return terms
