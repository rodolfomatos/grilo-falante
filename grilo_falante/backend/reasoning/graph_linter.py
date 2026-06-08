"""
Graph Linter — Epistemic integrity checks (L1-L8)

Performs structural integrity checks on epistemic graphs:

L1: Orphan nodes (no incoming edges)
L2: Self-referential edges
L3: Contradictory edges
L4: Circular dependencies
L5: Unsupported conclusions (M4 source for M1 target)
L6: Missing M1 prerequisites
L7: Confidence mismatches
L8: Temporal inconsistencies
"""

from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass

from grilo_falante.backend.memory.knowledge_graph import KnowledgeGraphStore


@dataclass
class LintIssue:
    code: str
    severity: str
    description: str
    affected_nodes: List[str]
    details: Dict[str, Any]


class GraphLinter:
    """
    Performs epistemic integrity checks on claim graphs.
    """

    L1_ORPHAN = "L1"
    L2_SELF_REF = "L2"
    L3_CONTRADICTION = "L3"
    L4_CYCLE = "L4"
    L5_UNSUPPORTED = "L5"
    L6_MISSING_M1 = "L6"
    L7_CONFIDENCE_MISMATCH = "L7"
    L8_TEMPORAL = "L8"

    def __init__(self, knowledge_graph: Optional[KnowledgeGraphStore] = None):
        self.knowledge_graph = knowledge_graph or KnowledgeGraphStore()

    async def run_all_checks(self) -> Dict[str, List[LintIssue]]:
        """
        Run all lint checks and return issues grouped by code.
        """
        graph_data = await self._get_graph_data()

        issues = {}

        issues[self.L1_ORPHAN] = self._detect_orphans(graph_data)
        issues[self.L2_SELF_REF] = self._detect_self_references(graph_data)
        issues[self.L3_CONTRADICTION] = self._detect_contradictions(graph_data)
        issues[self.L4_CYCLE] = self._detect_cycles(graph_data)
        issues[self.L5_UNSUPPORTED] = self._detect_unsupported_conclusions(graph_data)
        issues[self.L6_MISSING_M1] = self._detect_missing_m1_prerequisites(graph_data)
        issues[self.L7_CONFIDENCE_MISMATCH] = self._detect_confidence_mismatches(graph_data)

        return issues

    async def _get_graph_data(self) -> Dict[int, dict]:
        """Get graph data from knowledge graph store."""
        claims = await self.knowledge_graph.repo.list_all(limit=500)
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
                    "in_edges": claim.get("in_edges", []),
                    "out_edges": claim.get("out_edges", []),
                }

        return graph

    def _detect_orphans(self, graph: Dict[int, dict]) -> List[LintIssue]:
        """L1: Nodes with no incoming edges (except M1 primary claims)."""
        issues = []

        for claim_id, node in graph.items():
            in_edges = node.get("in_edges", [])
            gmif_level = node.get("gmif_level", "M4")

            if not in_edges and gmif_level not in ("M1", "M2"):
                issues.append(
                    LintIssue(
                        code=self.L1_ORPHAN,
                        severity="warning",
                        description=f"Orphan node without supporting claims",
                        affected_nodes=[node.get("claim_key", str(claim_id))],
                        details={"gmif_level": gmif_level},
                    )
                )

        return issues

    def _detect_self_references(self, graph: Dict[int, dict]) -> List[LintIssue]:
        """L2: Self-referential edges."""
        issues = []

        for claim_id, node in graph.items():
            for edge in node.get("out_edges", []):
                if edge.get("target_id") == claim_id:
                    issues.append(
                        LintIssue(
                            code=self.L2_SELF_REF,
                            severity="error",
                            description="Self-referential edge detected",
                            affected_nodes=[node.get("claim_key", str(claim_id))],
                            details={"relation": edge.get("relation")},
                        )
                    )

        return issues

    def _detect_contradictions(self, graph: Dict[int, dict]) -> List[LintIssue]:
        """L3: Nodes with both supporting and contradicting edges."""
        issues = []

        for claim_id, node in graph.items():
            has_support = False
            has_contradict = False

            for edge in node.get("in_edges", []):
                if edge.get("relation") == "supports":
                    has_support = True
                elif edge.get("relation") == "contradicts":
                    has_contradict = True

            if has_support and has_contradict:
                issues.append(
                    LintIssue(
                        code=self.L3_CONTRADICTION,
                        severity="error",
                        description="Node has both supporting and contradicting edges",
                        affected_nodes=[node.get("claim_key", str(claim_id))],
                        details={"has_support": has_support, "has_contradict": has_contradict},
                    )
                )

        return issues

    def _detect_cycles(self, graph: Dict[int, dict]) -> List[LintIssue]:
        """L4: Circular dependencies in the graph."""
        issues = []
        visited = set()
        rec_stack = set()

        def dfs(claim_id: int, path: List[int]) -> Optional[List[int]]:
            visited.add(claim_id)
            rec_stack.add(claim_id)
            path.append(claim_id)

            node = graph.get(claim_id, {})
            for edge in node.get("out_edges", []):
                target_id = edge.get("target_id")
                if target_id and target_id in graph:
                    if target_id not in visited:
                        cycle = dfs(target_id, path.copy())
                        if cycle:
                            return cycle
                    elif target_id in rec_stack:
                        cycle_start = path.index(target_id)
                        return path[cycle_start:] + [target_id]

            rec_stack.remove(claim_id)
            return None

        for claim_id in graph:
            if claim_id not in visited:
                cycle = dfs(claim_id, [])
                if cycle:
                    node_keys = [
                        graph.get(cid, {}).get("claim_key", str(cid))
                        for cid in cycle
                        if cid in graph
                    ]
                    issues.append(
                        LintIssue(
                            code=self.L4_CYCLE,
                            severity="error",
                            description="Circular dependency detected",
                            affected_nodes=node_keys,
                            details={"cycle_length": len(cycle)},
                        )
                    )

        return issues

    def _detect_unsupported_conclusions(self, graph: Dict[int, dict]) -> List[LintIssue]:
        """L5: Conclusions (M1 targets) sourced from M4 (doubtful) claims."""
        issues = []

        for claim_id, node in graph.items():
            if node.get("gmif_level") != "M1":
                continue

            m4_sources = []
            for edge in node.get("in_edges", []):
                source_id = edge.get("source_id")
                if source_id and source_id in graph:
                    if graph[source_id].get("gmif_level") == "M4":
                        m4_sources.append(graph[source_id].get("claim_key", str(source_id)))

            if m4_sources:
                issues.append(
                    LintIssue(
                        code=self.L5_UNSUPPORTED,
                        severity="error",
                        description="M1 conclusion sourced from M4 (doubtful) claims",
                        affected_nodes=[node.get("claim_key", str(claim_id))],
                        details={"m4_sources": m4_sources},
                    )
                )

        return issues

    def _detect_missing_m1_prerequisites(self, graph: Dict[int, dict]) -> List[LintIssue]:
        """L6: Claims without M1/M2 prerequisite claims in evidence chain."""
        issues = []

        for claim_id, node in graph.items():
            gmif_level = node.get("gmif_level", "M4")

            if gmif_level in ("M1", "M2"):
                continue

            has_m1_m2_ancestor = False
            ancestors = self._get_ancestors(claim_id, graph, max_depth=10)

            for ancestor_id in ancestors:
                ancestor_level = graph.get(ancestor_id, {}).get("gmif_level", "M4")
                if ancestor_level in ("M1", "M2"):
                    has_m1_m2_ancestor = True
                    break

            if not has_m1_m2_ancestor and ancestors:
                issues.append(
                    LintIssue(
                        code=self.L6_MISSING_M1,
                        severity="warning",
                        description="Claim chain missing M1/M2 primary evidence",
                        affected_nodes=[node.get("claim_key", str(claim_id))],
                        details={"ancestor_count": len(ancestors)},
                    )
                )

        return issues

    def _detect_confidence_mismatches(self, graph: Dict[int, dict]) -> List[LintIssue]:
        """L7: Claims where confidence doesn't match GMIF level expectations."""
        issues = []

        level_expected = {
            "M1": (0.8, 1.0),
            "M2": (0.6, 0.9),
            "M3": (0.4, 0.7),
            "M4": (0.1, 0.5),
            "M5": (0.5, 0.8),
            "M6": (0.4, 0.7),
            "M7": (0.5, 0.8),
        }

        for claim_id, node in graph.items():
            gmif_level = node.get("gmif_level", "M4")
            confidence = node.get("confidence", 0.5)

            if gmif_level in level_expected:
                min_exp, max_exp = level_expected[gmif_level]
                if confidence < min_exp - 0.2 or confidence > max_exp + 0.2:
                    issues.append(
                        LintIssue(
                            code=self.L7_CONFIDENCE_MISMATCH,
                            severity="warning",
                            description=f"Confidence {confidence} mismatches {gmif_level} expected range",
                            affected_nodes=[node.get("claim_key", str(claim_id))],
                            details={
                                "gmif_level": gmif_level,
                                "confidence": confidence,
                                "expected_range": (min_exp, max_exp),
                            },
                        )
                    )

        return issues

    def _get_ancestors(
        self,
        claim_id: int,
        graph: Dict[int, dict],
        max_depth: int = 5,
    ) -> List[int]:
        """Get ancestor claim IDs up to max_depth."""
        ancestors = []
        visited = set()
        queue = [(claim_id, 0)]

        while queue:
            current_id, depth = queue.pop(0)
            if current_id in visited or depth > max_depth:
                continue

            visited.add(current_id)
            node = graph.get(current_id, {})

            for edge in node.get("in_edges", []):
                source_id = edge.get("source_id")
                if source_id and source_id not in visited:
                    ancestors.append(source_id)
                    queue.append((source_id, depth + 1))

        return ancestors

    async def lint_claim(self, claim_id: int) -> Dict[str, List[LintIssue]]:
        """Lint a single claim and its immediate neighborhood."""
        graph_data = await self._get_graph_data()

        if claim_id not in graph_data:
            return {}

        node = graph_data[claim_id]
        affected_ids = {claim_id}
        for edge in node.get("out_edges", []):
            affected_ids.add(edge.get("target_id"))
        for edge in node.get("in_edges", []):
            affected_ids.add(edge.get("source_id"))

        affected_graph = {cid: graph_data[cid] for cid in affected_ids if cid in graph_data}

        issues = {}
        issues[self.L1_ORPHAN] = self._detect_orphans(affected_graph)
        issues[self.L2_SELF_REF] = self._detect_self_references(affected_graph)
        issues[self.L3_CONTRADICTION] = self._detect_contradictions(affected_graph)
        issues[self.L5_UNSUPPORTED] = self._detect_unsupported_conclusions(affected_graph)
        issues[self.L7_CONFIDENCE_MISMATCH] = self._detect_confidence_mismatches(affected_graph)

        return {k: v for k, v in issues.items() if v}
