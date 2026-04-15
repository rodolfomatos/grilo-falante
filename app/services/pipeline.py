"""
Pipeline - Grilo Falante Analysis Pipeline

Orchestrates the full analysis pipeline:
- PHASE 0: Objeto Digital
- PHASE 1: Extração de Claims
- PHASE 2: GMIF Classification
- PHASE 3: Construção do Grafo
- PHASE 4: MemPalace Storage
"""

import hashlib
import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

from app.data.memory.graph.gmif import (
    get_gmif_classifier,
    GMIFClassifier,
    GMIFClassification,
)
from app.data.memory.graph.claims import get_claims_extractor, Claim
from app.data.memory.graph.builder import get_graph_builder, GraphBuilder
from app.data.memory.graph.models import GraphNode, EpistemicGraph
from app.data.memory.semantic import get_semantic_memory, SemanticMemory

logger = logging.getLogger(__name__)


@dataclass
class ObjetoDigital:
    """The digital object being analysed."""
    id: str
    type: str  # text, chat, article, decision
    name: str
    boundaries: List[str]  # What IS included
    exclusions: List[str]  # What is NOT included
    authority: str  # Who is responsible
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "boundaries": self.boundaries,
            "exclusions": self.exclusions,
            "authority": self.authority,
            "metadata": self.metadata,
        }


@dataclass
class AnalysisResult:
    """Result of analysis."""
    objeto_digital: ObjetoDigital
    claims: List[Claim]
    graph: EpistemicGraph
    classifications: Dict[str, GMIFClassification]
    gf_ids: List[str]
    metadata: Dict
    
    def to_dict(self) -> Dict:
        return {
            "objeto_digital": self.objeto_digital.to_dict(),
            "total_claims": len(self.claims),
            "classifications": {
                k: {"type": v.type.value, "description": v.description}
                for k, v in self.classifications.items()
            },
            "gf_ids": self.gf_ids,
            "metadata": self.metadata,
            "graph_summary": {
                "nodes": len(self.graph.nodes),
                "edges": len(self.graph.edges),
            },
        }


class Pipeline:
    """
    Grilo Falante Analysis Pipeline.
    
    Applies the regime principles to any content.
    """
    
    # Valid content types
    VALID_TYPES = ["text", "chat", "article", "decision", "code"]
    
    def __init__(self):
        self.classifier = get_gmif_classifier()
        self.extractor = get_claims_extractor()
        self.builder = get_graph_builder()
        self.memory = get_semantic_memory()
        self._internal_graph = None  # Track built graph
    
    async def analyse(
        self,
        content: Any,
        content_type: str,
        metadata: Optional[Dict] = None,
    ) -> AnalysisResult:
        """
        Run full analysis pipeline.
        
        Args:
            content: The content to analyse (str, List[Dict], Dict)
            content_type: text, chat, article, decision
            metadata: Additional metadata
            
        Returns:
            AnalysisResult with full details
        """
        metadata = metadata or {}
        
        # PHASE 0: Objeto Digital
        objeto = self._create_objeto_digital(content, content_type, metadata)
        
        logger.info(f"PHASE 0: Objeto Digital created: {objeto.id}")
        
        # PHASE 1: Extração de Claims
        claims = self._extract_claims(content, content_type, metadata)
        
        logger.info(f"PHASE 1: Extracted {len(claims)} claims")
        
        # PHASE 2: GMIF Classification
        classifications = self._classify_claims(claims, metadata)
        
        logger.info(f"PHASE 2: Classified claims")
        
        # PHASE 3: Construção do Grafo
        graph = self._build_graph(claims, content_type, metadata)
        
        # Store internal graph reference BEFORE storage
        self._internal_graph = graph
        
        logger.info(f"PHASE 3: Built graph with {len(graph.nodes)} nodes")
        
        # PHASE 4: MemPalace Storage
        gf_ids = self._store_in_memory(objeto, claims, classifications, metadata)
        
        logger.info(f"PHASE 4: Stored {len(gf_ids)} claims in memory")
        
        return AnalysisResult(
            objeto_digital=objeto,
            claims=claims,
            graph=graph,
            classifications=classifications,
            gf_ids=gf_ids,
            metadata={
                "content_type": content_type,
                "timestamp": datetime.now().isoformat(),
                **metadata,
            },
        )
    
    def _create_objeto_digital(
        self,
        content: Any,
        content_type: str,
        metadata: Dict,
    ) -> ObjetoDigital:
        """PHASE 0: Create Objeto Digital (lock ontológico)."""
        # Generate ID from content hash
        content_str = str(content)
        content_hash = hashlib.sha256(content_str.encode()).hexdigest()[:12]
        
        # Get metadata
        name = metadata.get("name", f"{content_type}_{content_hash}")
        authority = metadata.get("authority", "unknown")
        boundaries = metadata.get("boundaries", [])
        exclusions = metadata.get("exclusions", [])
        
        # Validate content type
        if content_type not in self.VALID_TYPES:
            logger.warning(f"Unknown content type: {content_type}, using 'text'")
            content_type = "text"
        
        return ObjetoDigital(
            id=f"OD-{content_hash}",
            type=content_type,
            name=name,
            boundaries=boundaries,
            exclusions=exclusions,
            authority=authority,
            metadata={
                "content_hash": content_hash,
                **metadata,
            },
        )
    
    def _extract_claims(
        self,
        content: Any,
        content_type: str,
        metadata: Dict,
    ) -> List[Claim]:
        """PHASE 1: Extract claims from content."""
        session_id = metadata.get("session_id", "default")
        
        if content_type == "chat":
            messages = content if isinstance(content, list) else metadata.get("messages", [])
            return self.extractor.extract_from_chat(messages, session_id)
        elif content_type == "article":
            article = content if isinstance(content, dict) else metadata.get("article", {})
            return self.extractor.extract_from_article(article, metadata.get("doi"))
        elif content_type == "decision":
            decision = content if isinstance(content, dict) else metadata.get("decision", {})
            return self.extractor.extract_from_decision(decision)
        else:
            text = str(content)
            return self.extractor.extract_from_text(text, session_id)
    
    def _classify_claims(
        self,
        claims: List[Claim],
        metadata: Dict,
    ) -> Dict[str, GMIFClassification]:
        """PHASE 2: Classify claims with GMIF."""
        classifications = {}
        
        for claim in claims:
            classification = self.classifier.classify(
                claim=claim.text,
                confidence=metadata.get("confidence", 0.5),
                sources=[{"id": a, "type": "extracted"} for a in claim.anchors],
                risks=metadata.get("risks", []),
                assumptions=metadata.get("assumptions", []),
            )
            classifications[claim.id] = classification
        
        return classifications
    
    def _build_graph(
        self,
        claims: List[Claim],
        content_type: str,
        metadata: Dict,
    ) -> EpistemicGraph:
        """PHASE 3: Build epistemic graph."""
        return self.builder.build_from_claims(claims, metadata)
    
    def _store_in_memory(
        self,
        objeto: ObjetoDigital,
        claims: List[Claim],
        classifications: Dict[str, GMIFClassification],
        metadata: Dict,
    ) -> List[str]:
        """PHASE 4: Store in MemPalace."""
        gf_ids = []
        
        for claim in claims:
            classification = classifications.get(claim.id)
            if not classification:
                continue
            
            # Get GF-ID from internal graph
            node = self._internal_graph.find_by_external_id(claim.id) if self._internal_graph else None
            gf_id = node.gf_id if node and hasattr(node, 'gf_id') else None
            
            if not gf_id:
                continue
            
            gf_ids.append(gf_id)
            
            # Store in memory
            self.memory.add_claim(
                gf_id=gf_id,
                claim_text=claim.text,
                gmif_type=classification.type.value,
                wing=metadata.get("wing", "wing_conversas"),
                room=objeto.type,
                sources=claim.anchors,
                metadata={
                    "objeto_id": objeto.id,
                    **metadata,
                },
            )
        
        return gf_ids
    
    def search_memory(
        self,
        query: str,
        wing: Optional[str] = None,
    ) -> List[Dict]:
        """Search stored memories."""
        return self.memory.search(query, wing=wing)
    
    def get_gf_id_details(self, gf_id: str) -> Optional[Dict]:
        """Get details about a specific GF-ID."""
        # Search in memory
        record = self.memory.get_by_gf_id(gf_id)
        if record:
            return record
        
        # Search in graph
        node = self.builder.graph.find_by_gf_id(gf_id)
        if node:
            return node.to_dict()
        
        return None


# Singleton
_pipeline: Optional[Pipeline] = None


def get_pipeline() -> Pipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = Pipeline()
    return _pipeline