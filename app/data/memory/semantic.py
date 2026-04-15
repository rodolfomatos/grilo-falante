"""
Semantic Memory - MemPalace Integration

Layer over MemPalace for semantic storage and retrieval.
"""

import logging
import os
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import MemPalace - gracefully degrade if not available
try:
    from mempalace.searcher import search_memories
    from mempalace.knowledge_graph import KnowledgeGraph
    MEMPALACE_AVAILABLE = True
except ImportError:
    MEMPALACE_AVAILABLE = False
    logger.warning("MemPalace not available - using fallback")


class SemanticMemory:
    """
    Semantic memory with MemPalace integration.
    
    When MemPalace is available:
    - Uses ChromaDB for storage
    - Semantic search
    - Knowledge graph (temporal)
    
    Fallback:
    - JSON file storage
    - Simple in-memory
    """
    
    # Default wings for Grilo Falante
    DEFAULT_WINGS = {
        "wing_grilo_falante": "regime",
        "wing_conversas": "chat sessions",
        "wing_artigos": "analysed articles",
        "wing_decisoes": "decisions",
    }
    
    # Default halls (memory types)
    DEFAULT_HALLS = {
        "hall_facts": "decisions made, choices locked",
        "hall_events": "sessions, milestones",
        "hall_discoveries": "breakthroughs, insights",
        "hall_preferences": "habits, likes, opinions",
        "hall_advice": "recommendations, solutions",
    }
    
    def __init__(self, palace_path: Optional[str] = None):
        self.palace_path = palace_path or os.path.expanduser("~/.mempalace")
        self.available = MEMPALACE_AVAILABLE
        self.fallback_storage: List[Dict] = []
        
        # Try to init MemPalace
        if self.available:
            try:
                self.kg = KnowledgeGraph()
            except Exception as e:
                logger.warning(f"Failed to init MemPalace KG: {e}")
                self.available = False
    
    def add_claim(
        self,
        gf_id: str,
        claim_text: str,
        gmif_type: str,
        wing: str = "wing_conversas",
        room: str = "default",
        hall: str = "hall_facts",
        sources: Optional[List[str]] = None,
        metadata: Optional[Dict] = None,
    ) -> bool:
        """
        Add a claim to memory.
        
        Args:
            gf_id: The GF-ID
            claim_text: The claim text
            gmif_type: M1-M7
            wing: Wing (category)
            room: Room (topic)
            hall: Hall (memory type)
            sources: Source references
            metadata: Additional metadata
            
        Returns:
            True if successful
        """
        metadata = metadata or {}
        sources = sources or []
        
        record = {
            "gf_id": gf_id,
            "claim": claim_text,
            "gmif_type": gmif_type,
            "wing": wing,
            "room": room,
            "hall": hall,
            "sources": sources,
            "metadata": metadata,
            "created_at": datetime.now().isoformat(),
        }
        
        if self.available:
            try:
                # Use MemPalace
                self.kg.add_triple(
                    entity1=gf_id,
                    relation="has_claim",
                    entity2=claim_text[:50],
                    valid_from=datetime.now().isoformat(),
                )
                return True
            except Exception as e:
                logger.warning(f"MemPalace add failed: {e}")
        
        # Fallback
        self.fallback_storage.append(record)
        return True
    
    def search(
        self,
        query: str,
        wing: Optional[str] = None,
        room: Optional[str] = None,
        hall: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict]:
        """
        Search memory.
        
        Args:
            query: Search query
            wing: Filter by wing
            room: Filter by room
            hall: Filter by hall
            limit: Max results
            
        Returns:
            List of matching records
        """
        if self.available:
            try:
                results = search_memories(
                    query,
                    palace_path=self.palace_path,
                    n_results=limit,
                )
                return results
            except Exception as e:
                logger.warning(f"MemPalace search failed: {e}")
        
        # Fallback: simple text search
        results = []
        query_lower = query.lower()
        
        for record in self.fallback_storage:
            # Filter
            if wing and record.get("wing") != wing:
                continue
            if room and record.get("room") != room:
                continue
            if hall and record.get("hall") != hall:
                continue
            
            # Text search
            if query_lower in record.get("claim", "").lower():
                results.append(record)
            
            if len(results) >= limit:
                break
        
        return results
    
    def get_by_gf_id(self, gf_id: str) -> Optional[Dict]:
        """Get a claim by GF-ID."""
        for record in self.fallback_storage:
            if record.get("gf_id") == gf_id:
                return record
        return None
    
    def list_wings(self) -> List[str]:
        """List available wings."""
        if self.available:
            try:
                # Get wings from MemPalace
                return list(self.DEFAULT_WINGS.keys())
            except:
                pass
        return list(self.DEFAULT_WINGS.keys())
    
    def get_stats(self) -> Dict:
        """Get memory statistics."""
        return {
            "available": self.available,
            "palace_path": self.palace_path,
            "total_claims": len(self.fallback_storage),
            "wings": list(self.DEFAULT_WINGS.keys()),
            "halls": list(self.DEFAULT_HALLS.keys()),
        }


# Singleton
_memory: Optional[SemanticMemory] = None


def get_semantic_memory(palace_path: Optional[str] = None) -> SemanticMemory:
    global _memory
    if _memory is None:
        _memory = SemanticMemory(palace_path)
    return _memory