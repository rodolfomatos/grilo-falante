"""
Memory Services — Vector and graph-based retrieval

Includes:
- VectorIndex: pgvector similarity search
- KnowledgeGraphStore: Graph-based knowledge storage
- HybridRetriever: Combined semantic + epistemic scoring
- MemPalaceCache: Fast semantic cache using MemPalace (ChromaDB)
- HybridCacheRetriever: MemPalace + HybridRetriever combined
"""

from grilo_falante.backend.memory.vector_index import VectorIndex
from grilo_falante.backend.memory.knowledge_graph import KnowledgeGraphStore
from grilo_falante.backend.memory.hybrid_retrieval import HybridRetriever
from grilo_falante.backend.memory.mempalace_cache import (
    MemPalaceCache,
    HybridCacheRetriever,
    MEMPALACE_AVAILABLE,
)

__all__ = [
    "VectorIndex",
    "KnowledgeGraphStore",
    "HybridRetriever",
    "MemPalaceCache",
    "HybridCacheRetriever",
    "MEMPALACE_AVAILABLE",
]
