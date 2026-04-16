"""
Repository Model - RAG/FAQ Repository definitions.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RepositoryType(str, Enum):
    """Types of repositories."""
    FAQ = "faq"
    KNOWLEDGE_BASE = "knowledge_base"
    DOCUMENTS = "documents"
    CUSTOM = "custom"


class RepositoryStatus(str, Enum):
    """Repository status."""
    ACTIVE = "active"
    INDEXING = "indexing"
    ERROR = "error"
    INACTIVE = "inactive"


class RepositoryBase(BaseModel):
    """Base repository properties."""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="")
    repository_type: RepositoryType = RepositoryType.KNOWLEDGE_BASE
    plugin_name: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

    # Embeddings config
    embedding_model: str = "BAAI/bge-m3"
    chunk_size: int = 512
    chunk_overlap: int = 50

    # OpenDataLoader config
    use_opendataloader: bool = True
    extract_tables: bool = True
    extract_formulas: bool = False
    enable_ocr: bool = False


class RepositoryCreate(RepositoryBase):
    """Repository creation request."""
    pass


class RepositoryUpdate(BaseModel):
    """Repository update request."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    repository_type: Optional[RepositoryType] = None
    plugin_name: Optional[str] = None
    tags: Optional[List[str]] = None
    embedding_model: Optional[str] = None
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None
    status: Optional[RepositoryStatus] = None
    is_active: Optional[bool] = None


class RepositoryInDB(RepositoryBase):
    """Repository as stored in database."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: RepositoryStatus = RepositoryStatus.ACTIVE
    is_active: bool = True
    version: int = 1
    total_chunks: int = 0
    total_documents: int = 0
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_indexed_at: Optional[datetime] = None
    last_error: Optional[str] = None


class Repository(RepositoryBase):
    """Repository as returned by API."""
    id: str
    status: RepositoryStatus
    is_active: bool
    version: int
    total_chunks: int
    total_documents: int
    created_at: datetime
    updated_at: datetime
    last_indexed_at: Optional[datetime] = None
    last_error: Optional[str] = None

    class Config:
        from_attributes = True


class Chunk(BaseModel):
    """A chunk of content from a repository."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    repository_id: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    chunk_index: int
    document_name: Optional[str] = None
    page_number: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.now)


class Document(BaseModel):
    """A document uploaded to a repository."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    repository_id: str
    filename: str
    file_type: str
    file_size: int
    status: str = "pending"  # pending, processing, processed, error
    chunks_created: int = 0
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None


class FAQItem(BaseModel):
    """A FAQ Q&A item."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    repository_id: str
    question: str
    answer: str
    tags: List[str] = Field(default_factory=list)
    gmif_level: str = "M3"
    confidence: float = 0.5
    is_approved: bool = False
    source_chunk_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class IngestionRequest(BaseModel):
    """Request to ingest content into a repository."""
    document_id: Optional[str] = None
    content: Optional[str] = None
    url: Optional[str] = None
    process_with_feynman: bool = True
    feynman_levels: List[str] = Field(default_factory=lambda: ["F1", "F2", "F3"])


class IngestionResult(BaseModel):
    """Result of an ingestion operation."""
    success: bool
    document_id: Optional[str] = None
    chunks_created: int = 0
    faq_items_created: int = 0
    gaps_detected: int = 0
    error: Optional[str] = None
    processing_details: Dict[str, Any] = Field(default_factory=dict)


class SearchRequest(BaseModel):
    """Request to search a repository."""
    query: str
    repository_id: Optional[str] = None
    limit: int = 10
    include_faq: bool = True
    include_chunks: bool = True


class SearchResult(BaseModel):
    """Result of a search operation."""
    query: str
    results: List[Dict[str, Any]]
    total_results: int
    repository_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
