"""
Graph Data Models

Nodes and edges for the epistemic graph.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from uuid import uuid4


@dataclass
class GraphNode:
    """A node in the epistemic graph."""
    id: str
    node_type: str  # claim, entity, source, session
    label: str
    properties: Dict = field(default_factory=dict)
    gmif_type: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    # External references
    external_id: Optional[str] = None
    gf_id: Optional[str] = None  # The GF-ID for claims
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "node_type": self.node_type,
            "label": self.label,
            "properties": self.properties,
            "gmif_type": self.gmif_type,
            "external_id": self.external_id,
            "gf_id": self.gf_id,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class GraphEdge:
    """An edge in the epistemic graph."""
    id: str
    source_id: str
    target_id: str
    relation_type: str  # supports, contradicts, derives_from, similar_to
    confidence: float = 1.0
    evidence_type: str = "EXTRACTED"  # EXTRACTED, INFERRED, DERIVED
    properties: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type,
            "confidence": self.confidence,
            "evidence_type": self.evidence_type,
            "properties": self.properties,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class EpistemicGraph:
    """Complete epistemic graph."""
    nodes: List[GraphNode] = field(default_factory=list)
    edges: List[GraphEdge] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    
    def add_node(self, node: GraphNode) -> None:
        self.nodes.append(node)
    
    def add_edge(self, edge: GraphEdge) -> None:
        self.edges.append(edge)
    
    def find_node(self, node_id: str) -> Optional[GraphNode]:
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None
    
    def find_by_gf_id(self, gf_id: str) -> Optional[GraphNode]:
        for node in self.nodes:
            if node.gf_id == gf_id:
                return node
        return None
    
    def find_by_external_id(self, external_id: str) -> Optional[GraphNode]:
        for node in self.nodes:
            if node.external_id == external_id:
                return node
        return None
    
    def get_claims(self) -> List[GraphNode]:
        return [n for n in self.nodes if n.node_type == "claim"]
    
    def get_sources(self) -> List[GraphNode]:
        return [n for n in self.nodes if n.node_type == "source"]
    
    def get_dependencies(self, claim_id: str) -> List[GraphNode]:
        """Get claims this claim depends on."""
        dependencies = []
        for edge in self.edges:
            if edge.source_id == claim_id and edge.relation_type == "derives_from":
                target = self.find_node(edge.target_id)
                if target:
                    dependencies.append(target)
        return dependencies
    
    def to_dict(self) -> Dict:
        return {
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
            "metadata": self.metadata,
        }


@dataclass
class GFID:
    """Grilo Falante Identifier."""
    prefix: str = "GF"
    date: str = ""  # YYMMDD
    gmif_type: str = ""  # M1-M7
    hash: str = ""  # Short hash
    
    @classmethod
    def generate(cls, gmif_type: str, content_hash: str) -> "GFID":
        date = datetime.now().strftime("%y%m%d")
        short_hash = content_hash[:6] if len(content_hash) >= 6 else content_hash
        return cls(
            date=date,
            gmif_type=gmif_type,
            hash=short_hash,
        )
    
    def __str__(self) -> str:
        return f"{self.prefix}-{self.date}-{self.gmif_type}-{self.hash}"
    
    def to_dict(self) -> Dict:
        return {
            "prefix": self.prefix,
            "date": self.date,
            "gmif_type": self.gmif_type,
            "hash": self.hash,
        }