"""
Graph Builder - Builds epistemic graph from content

Creates nodes and edges from content with GMIF classification.
"""

import hashlib
import logging
from typing import List, Dict, Optional
from datetime import datetime
from uuid import uuid4

from app.data.memory.graph.gmif import (
    get_gmif_classifier, 
    GMIFClassifier, 
    GMIFType,
    GMIFClassification,
)
from app.data.memory.graph.claims import ClaimsExtractor, Claim, get_claims_extractor
from app.data.memory.graph.models import GraphNode, GraphEdge, EpistemicGraph, GFID

logger = logging.getLogger(__name__)


class GraphBuilder:
    """
    Builds and maintains the epistemic graph.
    
    Creates nodes and edges from content with GMIF classification.
    """
    
    def __init__(self):
        self.classifier = get_gmif_classifier()
        self.extractor = get_claims_extractor()
    
    def build_from_text(
        self,
        text: str,
        content_type: str = "text",
        metadata: Optional[Dict] = None,
    ) -> EpistemicGraph:
        """
        Build graph from plain text.
        
        Args:
            text: The text content
            content_type: text, chat, article, decision
            metadata: Additional metadata
            
        Returns:
            EpistemicGraph with nodes and edges
        """
        graph = EpistemicGraph()
        metadata = metadata or {}
        
        # Generate session/entity ID
        content_hash = hashlib.sha256(text.encode()).hexdigest()[:8]
        session_id = metadata.get("session_id", f"session_{content_hash}")
        
        # Create session node
        session_node = GraphNode(
            id=str(uuid4()),
            node_type="session",
            label=f"Session: {session_id}",
            properties={
                "content_type": content_type,
                "content_hash": content_hash,
                **metadata,
            },
        )
        graph.add_node(session_node)
        
        # Extract claims based on content type
        if content_type == "chat":
            messages = metadata.get("messages", [])
            claims = self.extractor.extract_from_chat(messages, session_id)
        elif content_type == "article":
            claims = self.extractor.extract_from_article(
                metadata.get("article", {}),
                metadata.get("doi"),
            )
        elif content_type == "decision":
            claims = self.extractor.extract_from_decision(metadata.get("decision", {}))
        else:
            claims = self.extractor.extract_from_text(text, session_id)
        
        # Process each claim
        for claim in claims:
            # Classify with GMIF
            classification = self.classifier.classify(
                claim=claim.text,
                confidence=metadata.get("confidence", 0.5),
                sources=[{"id": a, "type": "extracted"} for a in claim.anchors],
                risks=metadata.get("risks", []),
                assumptions=metadata.get("assumptions", []),
            )
            
            # Generate GF-ID
            gf_id = str(GFID.generate(
                gmif_type=classification.type.value,
                content_hash=content_hash + claim.id,
            ))
            
            # Create claim node
            claim_node = GraphNode(
                id=str(uuid4()),
                node_type="claim",
                label=claim.text[:100],
                properties={
                    "claim_id": claim.id,
                    "claim_text": claim.text,
                    "claim_type": claim.type,
                    "confidence": classification.confidence,
                },
                gmif_type=classification.type.value,
                external_id=claim.id,
                gf_id=gf_id,
            )
            graph.add_node(claim_node)
            
            # Link to session
            edge = GraphEdge(
                id=str(uuid4()),
                source_id=session_node.id,
                target_id=claim_node.id,
                relation_type="contains",
                evidence_type="EXTRACTED",
            )
            graph.add_edge(edge)
            
            # Add dependency edges
            for dep_id in claim.dependencies:
                dep_node = graph.find_node(dep_id)
                if dep_node:
                    dep_edge = GraphEdge(
                        id=str(uuid4()),
                        source_id=claim_node.id,
                        target_id=dep_node.id,
                        relation_type="derives_from",
                        evidence_type="INFERRED",
                    )
                    graph.add_edge(dep_edge)
        
        graph.metadata = {
            "content_type": content_type,
            "total_claims": len(claims),
            "session_id": session_id,
        }
        
        logger.info(f"Built graph with {len(graph.nodes)} nodes, {len(graph.edges)} edges")
        return graph
    
    def build_from_claims(
        self,
        claims: List[Claim],
        metadata: Optional[Dict] = None,
    ) -> EpistemicGraph:
        """Build graph from pre-extracted claims."""
        graph = EpistemicGraph()
        metadata = metadata or {}
        
        content_hash = metadata.get("content_hash", "")[:8]
        
        # Process claims
        for claim in claims:
            classification = self.classifier.classify(
                claim=claim.text,
                confidence=metadata.get("confidence", 0.5),
                sources=[{"id": a, "type": "extracted"} for a in claim.anchors],
                risks=metadata.get("risks", []),
                assumptions=metadata.get("assumptions", []),
            )
            
            gf_id = str(GFID.generate(
                gmif_type=classification.type.value,
                content_hash=content_hash + claim.id,
            ))
            
            claim_node = GraphNode(
                id=str(uuid4()),
                node_type="claim",
                label=claim.text[:100],
                properties={
                    "claim_id": claim.id,
                    "claim_text": claim.text,
                    "claim_type": claim.type,
                },
                gmif_type=classification.type.value,
                external_id=claim.id,
                gf_id=gf_id,
            )
            graph.add_node(claim_node)
        
        return graph
    
    def add_source(
        self,
        graph: EpistemicGraph,
        source: Dict,
    ) -> GraphNode:
        """Add a source node to graph."""
        source_node = GraphNode(
            id=str(uuid4()),
            node_type="source",
            label=source.get("label", source.get("reference", "source")),
            properties=source,
            external_id=source.get("id"),
        )
        graph.add_node(source_node)
        return source_node
    
    def add_relation(
        self,
        graph: EpistemicGraph,
        from_claim_id: str,
        to_claim_id: str,
        relation_type: str,
        confidence: float = 1.0,
    ) -> Optional[GraphEdge]:
        """Add relation between claims."""
        from_node = graph.find_node(from_claim_id)
        to_node = graph.find_node(to_claim_id)
        
        if not from_node or not to_node:
            return None
        
        edge = GraphEdge(
            id=str(uuid4()),
            source_id=from_node.id,
            target_id=to_node.id,
            relation_type=relation_type,
            confidence=confidence,
            evidence_type="INFERRED",
        )
        graph.add_edge(edge)
        return edge
    
    def get_graph_summary(self, graph: EpistemicGraph) -> Dict:
        """Get summary of graph."""
        claims = graph.get_claims()
        
        # Count by GMIF type
        type_counts = {}
        for claim in claims:
            gmif = claim.gmif_type or "unknown"
            type_counts[gmif] = type_counts.get(gmif, 0) + 1
        
        return {
            "total_nodes": len(graph.nodes),
            "total_edges": len(graph.edges),
            "total_claims": len(claims),
            "by_gmif_type": type_counts,
            "metadata": graph.metadata,
        }


# Singleton
_builder: Optional[GraphBuilder] = None


def get_graph_builder() -> GraphBuilder:
    global _builder
    if _builder is None:
        _builder = GraphBuilder()
    return _builder