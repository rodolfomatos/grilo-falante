"""
Knowledge Graph Store — Graph-based knowledge representation

Stores claims as nodes with typed edges representing:
- supports
- contradicts
- depends_on

Provides graph-based queries and traversal.
"""

from typing import List, Set, Optional, Dict, Any
from collections import defaultdict

from grilo_falante.backend.db.repositories import ClaimRepository


class KnowledgeGraphStore:
    """
    Knowledge graph for claims with typed relationships.
    """

    def __init__(self):
        self.repo = ClaimRepository()
        self._cache: Optional[Dict[int, dict]] = None
        self._edges_cache: Optional[list] = None

    def _build_graph(self, claims: List[dict]) -> Dict[int, dict]:
        """Build graph structure from claims list."""
        graph = {}
        for claim in claims:
            claim_id = claim.get("id")
            if claim_id:
                graph[claim_id] = {
                    "id": claim_id,
                    "claim_key": claim.get("claim_key", ""),
                    "claim_text": claim.get("claim_text", ""),
                    "gmif_level": claim.get("gmif_level", "M4"),
                    "confidence": claim.get("gmif_confidence", 0.5),
                    "in_edges": [],
                    "out_edges": [],
                }
        return graph

    async def get_neighbors(
        self,
        claim_id: int,
        depth: int = 1,
        relation_type: Optional[str] = None,
    ) -> List[dict]:
        """
        Get neighboring claims in the graph.
        """
        claims = await self.repo.list_all(limit=500)
        graph = self._build_graph(claims)

        if claim_id not in graph:
            return []

        visited = set()
        result = []
        queue = [(claim_id, 0)]

        while queue:
            current_id, current_depth = queue.pop(0)
            if current_id in visited or current_depth > depth:
                continue

            visited.add(current_id)

            if current_id != claim_id:
                result.append(graph.get(current_id))

            if current_depth < depth:
                for edge in graph.get(current_id, {}).get("out_edges", []):
                    neighbor_id = edge.get("target_id")
                    if relation_type is None or edge.get("relation") == relation_type:
                        queue.append((neighbor_id, current_depth + 1))

        return result

    async def get_supporting_claims(self, claim_id: int) -> List[dict]:
        """Get claims that support the given claim."""
        claims = await self.repo.list_all(limit=500)
        graph = self._build_graph(claims)

        supporting = []
        for claim in claims:
            source_id = claim.get("id")
            if source_id and source_id != claim_id:
                for edge in claim.get("out_edges", []):
                    if edge.get("target_id") == claim_id and edge.get("relation") == "supports":
                        supporting.append(claim)
                        break

        return supporting

    async def get_contradicting_claims(self, claim_id: int) -> List[dict]:
        """Get claims that contradict the given claim."""
        claims = await self.repo.list_all(limit=500)

        contradicting = []
        for claim in claims:
            if claim.get("id") == claim_id:
                continue
            for edge in claim.get("out_edges", []):
                if edge.get("target_id") == claim_id and edge.get("relation") == "contradicts":
                    contradicting.append(claim)
                    break

        return contradicting

    async def get_claim_ancestors(self, claim_id: int, max_depth: int = 5) -> List[dict]:
        """Get all ancestor claims (claims this claim depends on)."""
        claims = await self.repo.list_all(limit=500)
        graph = self._build_graph(claims)

        ancestors = []
        visited = set()
        queue = [(claim_id, 0)]

        while queue:
            current_id, current_depth = queue.pop(0)
            if current_id in visited or current_depth > max_depth:
                continue

            visited.add(current_id)

            node = graph.get(current_id, {})
            for edge in node.get("in_edges", []):
                source_id = edge.get("source_id")
                if source_id and source_id not in visited:
                    source_claim = graph.get(source_id)
                    if source_claim:
                        ancestors.append(source_claim)
                    queue.append((source_id, current_depth + 1))

        return ancestors

    async def get_claim_descendants(self, claim_id: int, max_depth: int = 5) -> List[dict]:
        """Get all descendant claims (claims that depend on this claim)."""
        claims = await self.repo.list_all(limit=500)
        graph = self._build_graph(claims)

        descendants = []
        visited = set()
        queue = [(claim_id, 0)]

        while queue:
            current_id, current_depth = queue.pop(0)
            if current_id in visited or current_depth > max_depth:
                continue

            visited.add(current_id)

            node = graph.get(current_id, {})
            for edge in node.get("out_edges", []):
                target_id = edge.get("target_id")
                if target_id and target_id not in visited:
                    target_claim = graph.get(target_id)
                    if target_claim:
                        descendants.append(target_claim)
                    queue.append((target_id, current_depth + 1))

        return descendants

    async def get_epistemic_score(self, claim_id: int) -> float:
        """
        Calculate epistemic score for a claim based on:
        - Number of supporting claims
        - Confidence level
        - Number of validations
        - Recency
        """
        claim = await self.repo.get_by_id(claim_id)
        if not claim:
            return 0.0

        base_confidence = claim.gmif_confidence or 0.5

        supporting = await self.get_supporting_claims(claim_id)
        supporting_score = min(len(supporting) * 0.1, 0.3)

        contradicting = await self.get_contradicting_claims(claim_id)
        contradiction_penalty = min(len(contradicting) * 0.15, 0.5)

        score = base_confidence + supporting_score - contradiction_penalty
        return max(0.0, min(1.0, score))
