"""
Grilo Falante Transition Validator — Graph-based Governance

This implements the "Governação por Grafos" rule:
- All governed reasoning must be anchored to a materialized graph
- The model must explicitly declare: graph used, current state, transition validated
- Progression without valid transition = BLOCK
"""

from dataclasses import dataclass
from typing import Optional

from .state import StateMachine


@dataclass
class TransitionResult:
    valid: bool
    from_node: str
    to_node: str
    graph_id: str
    message: str
    available_transitions: list[str]


@dataclass
class EpistemicGraph:
    graph_id: str
    name: str
    nodes: list
    edges: list


class TransitionValidator:
    """
    Validates transitions against epistemic graphs.

    For v3.0, this provides a simplified in-memory graph store
    that can be extended with the full graph system later.
    """

    def __init__(self, state_machine: StateMachine):
        self.state_machine = state_machine
        self._graphs: dict[str, EpistemicGraph] = {}
        self._transitions: dict[str, dict[str, list[str]]] = {}

    def register_graph(
        self, graph_id: str, name: str, nodes: list[str], edges: list[tuple[str, str]]
    ):
        """Register an epistemic graph with its valid transitions"""
        self._graphs[graph_id] = EpistemicGraph(
            graph_id=graph_id,
            name=name,
            nodes=nodes,
            edges=edges,
        )
        self._transitions[graph_id] = {}
        for from_node, to_node in edges:
            if from_node not in self._transitions[graph_id]:
                self._transitions[graph_id][from_node] = []
            self._transitions[graph_id][from_node].append(to_node)

    def is_valid_transition(self, graph_id: str, from_node: str, to_node: str) -> tuple[bool, str]:
        """Check if a transition is valid"""
        if graph_id not in self._transitions:
            return False, f"Graph '{graph_id}' not found"

        if from_node not in self._transitions[graph_id]:
            return False, f"Node '{from_node}' not found in graph '{graph_id}'"

        if to_node not in self._transitions[graph_id][from_node]:
            available = self._transitions[graph_id][from_node]
            return (
                False,
                f"No valid transition from '{from_node}' to '{to_node}'. Available: {available}",
            )

        return True, f"Valid transition: {from_node} -> {to_node}"

    def validate_transition(
        self, from_node: str, to_node: str, graph_id: str, auto_update_position: bool = True
    ) -> TransitionResult:
        """Validate a transition in an epistemic graph"""
        valid, message = self.is_valid_transition(graph_id, from_node, to_node)

        if valid and auto_update_position:
            self.state_machine.set_position(graph_id, to_node)

        available = self._transitions.get(graph_id, {}).get(from_node, [])
        available_strs = [f"{from_node}->{n}" for n in available]

        return TransitionResult(
            valid=valid,
            from_node=from_node,
            to_node=to_node,
            graph_id=graph_id,
            message=message,
            available_transitions=available_strs,
        )

    def validate_and_block(self, from_node: str, to_node: str, graph_id: str) -> TransitionResult:
        """Validate transition and return BLOCK if invalid"""
        result = self.validate_transition(from_node, to_node, graph_id)

        if not result.valid:
            result.message = f"BLOCK — {result.message}"

        return result

    def get_current_position(self) -> dict:
        """Get current position in epistemic graphs"""
        if self.state_machine.current_cycle is None:
            return {"error": "No active cycle"}

        ctx = self.state_machine.current_cycle
        return {
            "graph_id": ctx.current_graph,
            "node_id": ctx.current_node,
            "cycle_id": ctx.cycle_id,
        }

    def list_graphs(self) -> dict:
        """List all registered graphs"""
        graphs = {}
        for gid, graph in self._graphs.items():
            graphs[gid] = {
                "name": graph.name,
                "nodes": graph.nodes,
                "edges": [f"{e[0]}->{e[1]}" for e in graph.edges],
            }
        return graphs
