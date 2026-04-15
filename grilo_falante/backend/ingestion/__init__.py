"""
Ingestion Services — PDF parsing and shadow document generation
"""

from grilo_falante.backend.ingestion.pdf_ingestion import (
    PDFIngestionService,
    PDFParseResult,
    PDFChunk,
)
from grilo_falante.backend.ingestion.shadow_document_generator import (
    ShadowDocumentGenerator,
    GenerationResult,
)

__all__ = [
    "PDFIngestionService",
    "PDFParseResult",
    "PDFChunk",
    "ShadowDocumentGenerator",
    "GenerationResult",
]
