"""
RAG Index Service.

Provides RAG (Retrieval-Augmented Generation) indexing capabilities:
- Index chunks with embeddings
- Search through indexed content
- Manage FAQ items
- Integration with MemPalace (ChromaDB)

This service handles the complete pipeline:
1. Content → OpenDataLoader → Markdown/JSON
2. Markdown → Feynman F1/F2/F3 processing
3. Content → Chunking → Embedding → MemPalace index
"""

import json
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

MEMPALACE_AVAILABLE = False
try:
    import chromadb
    from chromadb.config import Settings
    MEMPALACE_AVAILABLE = True
    logger.info("ChromaDB (MemPalace) is available")
except ImportError:
    logger.warning(
        "ChromaDB not installed. RAG indexing will use in-memory storage. "
        "Install with: pip install chromadb"
    )


class RAGIndexService:
    """
    RAG Index Service for managing vector storage and retrieval.

    Provides:
    - Collection management
    - Document/chunk indexing
    - Similarity search
    - FAQ item management
    """

    def __init__(
        self,
        persist_directory: str = "/tmp/grilo_mem palace",
        collection_name: str = "grilo_falante",
    ):
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)

        self._client = None
        self._collections: Dict[str, Any] = {}
        self._in_memory_store: Dict[str, List[Dict]] = {}

        if MEMPALACE_AVAILABLE:
            self._initialize_chroma()
        else:
            logger.info("Using in-memory storage for RAG")

    def _initialize_chroma(self):
        """Initialize ChromaDB client and collections."""
        try:
            self._client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(anonymized_telemetry=False),
            )
            logger.info(f"ChromaDB initialized at {self.persist_directory}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self._client = None

    def get_or_create_collection(
        self,
        repository_id: str,
        metadata: Optional[Dict] = None,
    ) -> str:
        """
        Get or create a collection for a repository.

        Returns collection name.
        """
        if self._client:
            try:
                collection = self._client.get_or_create_collection(
                    name=f"repo_{repository_id}",
                    metadata=metadata or {"repository_id": repository_id},
                )
                self._collections[repository_id] = collection
                return collection.name
            except Exception as e:
                logger.error(f"Failed to create collection: {e}")

        if repository_id not in self._in_memory_store:
            self._in_memory_store[repository_id] = []

        return repository_id

    def index_chunks(
        self,
        repository_id: str,
        chunks: List[Dict[str, Any]],
        document_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Index chunks into the vector store.

        Args:
            repository_id: Repository ID
            chunks: List of chunk dicts with 'content' key
            document_name: Optional document source name

        Returns:
            Indexing result with chunk_ids and count
        """
        collection_name = self.get_or_create_collection(repository_id)

        chunk_ids = []
        embedded_content = []
        metadatas = []

        for i, chunk in enumerate(chunks):
            chunk_id = str(uuid.uuid4())
            chunk_ids.append(chunk_id)

            content = chunk.get("content", "")
            embedded_content.append(content)

            metadata = {
                "repository_id": repository_id,
                "chunk_index": chunk.get("chunk_index", i),
                "document_name": document_name or "unknown",
                "indexed_at": datetime.now().isoformat(),
            }
            if "metadata" in chunk:
                metadata.update(chunk["metadata"])

            metadatas.append(metadata)

        if self._client and collection_name in self._collections:
            try:
                collection = self._collections[collection_name]
                collection.add(
                    ids=chunk_ids,
                    documents=embedded_content,
                    metadatas=metadatas,
                )
                logger.info(f"Indexed {len(chunks)} chunks into {collection_name}")
            except Exception as e:
                logger.error(f"Failed to index chunks: {e}")
                self._fallback_index(repository_id, chunk_ids, embedded_content, metadatas)
        else:
            self._fallback_index(repository_id, chunk_ids, embedded_content, metadatas)

        return {
            "success": True,
            "chunks_indexed": len(chunks),
            "chunk_ids": chunk_ids,
            "collection": collection_name,
        }

    def _fallback_index(
        self,
        repository_id: str,
        chunk_ids: List[str],
        content: List[str],
        metadatas: List[Dict],
    ):
        """Fallback in-memory indexing."""
        for i, chunk_id in enumerate(chunk_ids):
            self._in_memory_store.setdefault(repository_id, []).append({
                "id": chunk_id,
                "content": content[i],
                "metadata": metadatas[i],
            })
        logger.info(f"Fallback indexed {len(chunk_ids)} chunks in memory")

    def search(
        self,
        repository_id: str,
        query: str,
        n_results: int = 5,
        where: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Search for similar content in a repository.

        Args:
            repository_id: Repository to search
            query: Search query
            n_results: Number of results to return
            where: Optional metadata filter

        Returns:
            Search results with documents and distances
        """
        if self._client and repository_id in self._collections:
            try:
                collection = self._collections[repository_id]
                results = collection.query(
                    query_texts=[query],
                    n_results=n_results,
                    where=where,
                )

                return {
                    "success": True,
                    "results": results.get("documents", [[]])[0],
                    "metadatas": results.get("metadatas", [[]])[0],
                    "distances": results.get("distances", [[]])[0],
                    "ids": results.get("ids", [[]])[0],
                }
            except Exception as e:
                logger.error(f"Search error: {e}")

        return self._fallback_search(repository_id, query, n_results)

    def _fallback_search(
        self,
        repository_id: str,
        query: str,
        n_results: int,
    ) -> Dict[str, Any]:
        """Fallback in-memory search using simple keyword matching."""
        docs = self._in_memory_store.get(repository_id, [])

        if not docs:
            return {
                "success": True,
                "results": [],
                "metadatas": [],
                "distances": [],
                "ids": [],
            }

        query_words = set(query.lower().split())
        scored = []

        for doc in docs:
            content_words = set(doc["content"].lower().split())
            overlap = len(query_words & content_words)
            if overlap > 0:
                score = overlap / max(len(query_words), 1)
                scored.append((score, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        top_results = scored[:n_results]

        return {
            "success": True,
            "results": [doc["content"] for _, doc in top_results],
            "metadatas": [doc["metadata"] for _, doc in top_results],
            "distances": [1 - score for score, _ in top_results],
            "ids": [doc["id"] for _, doc in top_results],
        }

    def delete_by_document(
        self,
        repository_id: str,
        document_name: str,
    ) -> Dict[str, Any]:
        """Delete all chunks from a specific document."""
        if self._client and repository_id in self._collections:
            try:
                collection = self._collections[repository_id]
                collection.delete(where={"document_name": document_name})
            except Exception as e:
                logger.error(f"Delete error: {e}")

        if repository_id in self._in_memory_store:
            self._in_memory_store[repository_id] = [
                d for d in self._in_memory_store[repository_id]
                if d["metadata"].get("document_name") != document_name
            ]

        return {
            "success": True,
            "document_name": document_name,
        }

    def get_stats(self, repository_id: str) -> Dict[str, Any]:
        """Get indexing statistics for a repository."""
        total_chunks = 0
        documents = set()

        if self._client and repository_id in self._collections:
            try:
                collection = self._collections[repository_id]
                total_chunks = collection.count()
            except Exception:
                pass

        if repository_id in self._in_memory_store:
            for doc in self._in_memory_store[repository_id]:
                total_chunks += 1
                doc_name = doc["metadata"].get("document_name", "unknown")
                documents.add(doc_name)

        return {
            "repository_id": repository_id,
            "total_chunks": total_chunks,
            "total_documents": len(documents),
            "documents": list(documents),
            "vector_store": "chroma" if self._client else "in_memory",
        }

    def clear_repository(self, repository_id: str) -> Dict[str, Any]:
        """Clear all indexed content for a repository."""
        if self._client and repository_id in self._collections:
            try:
                self._client.delete_collection(name=f"repo_{repository_id}")
                del self._collections[repository_id]
            except Exception as e:
                logger.error(f"Clear error: {e}")

        if repository_id in self._in_memory_store:
            del self._in_memory_store[repository_id]

        return {
            "success": True,
            "repository_id": repository_id,
            "message": f"Repository {repository_id} cleared",
        }


class FAQManager:
    """
    FAQ management for repositories.

    Stores and manages FAQ Q&A items extracted from content.
    """

    def __init__(self, storage_path: str = "/tmp/grilo_faqs"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        self._faqs: Dict[str, List[Dict]] = {}
        self._load_faqs()

    def _load_faqs(self):
        """Load FAQs from storage."""
        faq_file = os.path.join(self.storage_path, "faqs.json")
        if os.path.exists(faq_file):
            try:
                with open(faq_file, "r", encoding="utf-8") as f:
                    self._faqs = json.load(f)
                logger.info(f"Loaded {len(self._faqs)} FAQ entries")
            except Exception as e:
                logger.error(f"Failed to load FAQs: {e}")

    def _save_faqs(self):
        """Save FAQs to storage."""
        try:
            faq_file = os.path.join(self.storage_path, "faqs.json")
            with open(faq_file, "w", encoding="utf-8") as f:
                json.dump(self._faqs, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save FAQs: {e}")

    def add_faq(
        self,
        repository_id: str,
        question: str,
        answer: str,
        tags: Optional[List[str]] = None,
        source_chunk_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add a FAQ item to a repository."""
        faq_id = str(uuid.uuid4())

        faq = {
            "id": faq_id,
            "repository_id": repository_id,
            "question": question,
            "answer": answer,
            "tags": tags or [],
            "gmif_level": "M3",
            "confidence": 0.5,
            "is_approved": False,
            "source_chunk_id": source_chunk_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        self._faqs.setdefault(repository_id, []).append(faq)
        self._save_faqs()

        return faq

    def get_faqs(
        self,
        repository_id: str,
        approved_only: bool = False,
    ) -> List[Dict[str, Any]]:
        """Get FAQs for a repository."""
        faqs = self._faqs.get(repository_id, [])

        if approved_only:
            faqs = [f for f in faqs if f.get("is_approved", False)]

        return faqs

    def search_faqs(
        self,
        repository_id: str,
        query: str,
    ) -> List[Dict[str, Any]]:
        """Search FAQs by question/answer content."""
        faqs = self._faqs.get(repository_id, [])
        query_words = set(query.lower().split())

        results = []
        for faq in faqs:
            text = f"{faq['question']} {faq['answer']}".lower()
            if any(word in text for word in query_words):
                results.append(faq)

        return results

    def approve_faq(self, repository_id: str, faq_id: str) -> Optional[Dict]:
        """Approve a FAQ item."""
        faqs = self._faqs.get(repository_id, [])
        for faq in faqs:
            if faq["id"] == faq_id:
                faq["is_approved"] = True
                faq["updated_at"] = datetime.now().isoformat()
                self._save_faqs()
                return faq
        return None

    def delete_faq(self, repository_id: str, faq_id: str) -> bool:
        """Delete a FAQ item."""
        faqs = self._faqs.get(repository_id, [])
        original_len = len(faqs)
        self._faqs[repository_id] = [f for f in faqs if f["id"] != faq_id]

        if len(self._faqs[repository_id]) < original_len:
            self._save_faqs()
            return True
        return False
