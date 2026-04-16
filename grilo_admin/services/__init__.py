"""
Grilo Falante Admin Services.

Provides services for:
- OpenDataLoader PDF processing
- Feynman F1/F2/F3 processing
- RAG indexing
- Falacia detection and propagation
"""

from grilo_admin.services.opendataloader_service import OpenDataLoaderService
from grilo_admin.services.feynman_processor import FeynmanProcessor
from grilo_admin.services.rag_index_service import RAGIndexService
from grilo_admin.services.falacia_service import (
    FalaciaDetector,
    FalaciaPropagator,
    FalaciaCorrector,
)

__all__ = [
    "OpenDataLoaderService",
    "FeynmanProcessor",
    "RAGIndexService",
    "FalaciaDetector",
    "FalaciaPropagator",
    "FalaciaCorrector",
]