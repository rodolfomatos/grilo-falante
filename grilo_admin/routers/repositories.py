"""
Repositories Router - Repository/RAG CRUD endpoints.
"""

import logging
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from grilo_admin.auth import get_current_user, require_role
from grilo_admin.models import (
    Repository,
    RepositoryCreate,
    RepositoryUpdate,
    RepositoryStatus,
    RepositoryType,
    Document,
    IngestionRequest,
    IngestionResult,
    SearchRequest,
    SearchResult,
    User,
    UserRole,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/repositories", tags=["repositories"])

REPOSITORY_STORAGE_PATH = "/tmp/grilo_repositories"


class RepositoryManager:
    """Manages repository operations."""

    _repositories: Dict[str, Dict[str, Any]] = {}
    _documents: Dict[str, Dict[str, Any]] = {}
    _initialized = False

    @classmethod
    def initialize(cls):
        """Initialize storage directory."""
        if not cls._initialized:
            os.makedirs(REPOSITORY_STORAGE_PATH, exist_ok=True)
            cls._initialized = True

    @classmethod
    def create_repository(cls, data: RepositoryCreate) -> Repository:
        """Create a new repository."""
        cls.initialize()

        repo_id = str(uuid.uuid4())

        repo_dict = {
            "id": repo_id,
            "name": data.name,
            "description": data.description,
            "repository_type": data.repository_type.value,
            "plugin_name": data.plugin_name,
            "tags": data.tags,
            "embedding_model": data.embedding_model,
            "chunk_size": data.chunk_size,
            "chunk_overlap": data.chunk_overlap,
            "use_opendataloader": data.use_opendataloader,
            "extract_tables": data.extract_tables,
            "extract_formulas": data.extract_formulas,
            "enable_ocr": data.enable_ocr,
            "status": RepositoryStatus.ACTIVE.value,
            "is_active": True,
            "version": 1,
            "total_chunks": 0,
            "total_documents": 0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "last_indexed_at": None,
            "last_error": None,
        }

        cls._repositories[repo_id] = repo_dict

        repo_dir = os.path.join(REPOSITORY_STORAGE_PATH, repo_id)
        os.makedirs(repo_dir, exist_ok=True)

        logger.info(f"Created repository: {repo_id} ({data.name})")
        return cls._dict_to_repository(repo_dict)

    @classmethod
    def get_repository(cls, repo_id: str) -> Optional[Repository]:
        """Get a repository by ID."""
        repo_dict = cls._repositories.get(repo_id)
        if repo_dict:
            return cls._dict_to_repository(repo_dict)
        return None

    @classmethod
    def list_repositories(cls, plugin_name: Optional[str] = None) -> List[Repository]:
        """List all repositories."""
        repos = []
        for repo_dict in cls._repositories.values():
            if plugin_name and repo_dict.get("plugin_name") != plugin_name:
                continue
            repos.append(cls._dict_to_repository(repo_dict))
        return repos

    @classmethod
    def update_repository(cls, repo_id: str, updates: RepositoryUpdate) -> Optional[Repository]:
        """Update a repository."""
        repo_dict = cls._repositories.get(repo_id)
        if not repo_dict:
            return None

        update_data = updates.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                if key == "repository_type":
                    repo_dict[key] = value.value
                else:
                    repo_dict[key] = value

        repo_dict["updated_at"] = datetime.now().isoformat()
        cls._repositories[repo_id] = repo_dict

        logger.info(f"Updated repository: {repo_id}")
        return cls._dict_to_repository(repo_dict)

    @classmethod
    def delete_repository(cls, repo_id: str) -> bool:
        """Delete a repository."""
        if repo_id not in cls._repositories:
            return False

        del cls._repositories[repo_id]

        repo_dir = os.path.join(REPOSITORY_STORAGE_PATH, repo_id)
        if os.path.exists(repo_dir):
            import shutil
            shutil.rmtree(repo_dir)

        logger.info(f"Deleted repository: {repo_id}")
        return True

    @classmethod
    def add_document(cls, repo_id: str, filename: str, file_type: str, file_size: int) -> Document:
        """Add a document to a repository."""
        doc_id = str(uuid.uuid4())

        doc_dict = {
            "id": doc_id,
            "repository_id": repo_id,
            "filename": filename,
            "file_type": file_type,
            "file_size": file_size,
            "status": "pending",
            "chunks_created": 0,
            "error_message": None,
            "created_at": datetime.now().isoformat(),
            "processed_at": None,
        }

        cls._documents[doc_id] = doc_dict
        return cls._dict_to_document(doc_dict)

    @classmethod
    def get_document(cls, doc_id: str) -> Optional[Document]:
        """Get a document by ID."""
        doc_dict = cls._documents.get(doc_id)
        if doc_dict:
            return cls._dict_to_document(doc_dict)
        return None

    @classmethod
    def list_documents(cls, repo_id: str) -> List[Document]:
        """List documents in a repository."""
        docs = []
        for doc_dict in cls._documents.values():
            if doc_dict.get("repository_id") == repo_id:
                docs.append(cls._dict_to_document(doc_dict))
        return docs

    @classmethod
    def _dict_to_repository(cls, d: Dict[str, Any]) -> Repository:
        """Convert dict to Repository model."""
        return Repository(
            id=d["id"],
            name=d["name"],
            description=d.get("description", ""),
            repository_type=RepositoryType(d.get("repository_type", "knowledge_base")),
            plugin_name=d.get("plugin_name"),
            tags=d.get("tags", []),
            embedding_model=d.get("embedding_model", "BAAI/bge-m3"),
            chunk_size=d.get("chunk_size", 512),
            chunk_overlap=d.get("chunk_overlap", 50),
            use_opendataloader=d.get("use_opendataloader", True),
            extract_tables=d.get("extract_tables", True),
            extract_formulas=d.get("extract_formulas", False),
            enable_ocr=d.get("enable_ocr", False),
            status=RepositoryStatus(d.get("status", "active")),
            is_active=d.get("is_active", True),
            version=d.get("version", 1),
            total_chunks=d.get("total_chunks", 0),
            total_documents=d.get("total_documents", 0),
            created_at=datetime.fromisoformat(d["created_at"]) if isinstance(d["created_at"], str) else d["created_at"],
            updated_at=datetime.fromisoformat(d["updated_at"]) if isinstance(d["updated_at"], str) else d["updated_at"],
            last_indexed_at=datetime.fromisoformat(d["last_indexed_at"]) if d.get("last_indexed_at") else None,
            last_error=d.get("last_error"),
        )

    @classmethod
    def _dict_to_document(cls, d: Dict[str, Any]) -> Document:
        """Convert dict to Document model."""
        return Document(
            id=d["id"],
            repository_id=d["repository_id"],
            filename=d["filename"],
            file_type=d["file_type"],
            file_size=d["file_size"],
            status=d.get("status", "pending"),
            chunks_created=d.get("chunks_created", 0),
            error_message=d.get("error_message"),
            created_at=datetime.fromisoformat(d["created_at"]) if isinstance(d["created_at"], str) else d["created_at"],
            processed_at=datetime.fromisoformat(d["processed_at"]) if d.get("processed_at") else None,
        )


@router.post("", response_model=Repository, status_code=status.HTTP_201_CREATED)
async def create_repository(
    data: RepositoryCreate,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Create a new repository. Admin only.
    """
    return RepositoryManager.create_repository(data)


@router.get("", response_model=List[Repository])
async def list_repositories(
    plugin_name: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """
    List all repositories. Filter by plugin_name optional.
    """
    return RepositoryManager.list_repositories(plugin_name=plugin_name)


@router.get("/{repository_id}", response_model=Repository)
async def get_repository(
    repository_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific repository by ID.
    """
    repo = RepositoryManager.get_repository(repository_id)
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository '{repository_id}' not found",
        )
    return repo


@router.put("/{repository_id}", response_model=Repository)
async def update_repository(
    repository_id: str,
    updates: RepositoryUpdate,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Update a repository. Admin only.
    """
    repo = RepositoryManager.update_repository(repository_id, updates)
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository '{repository_id}' not found",
        )
    return repo


@router.delete("/{repository_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_repository(
    repository_id: str,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Delete a repository. Admin only.
    """
    deleted = RepositoryManager.delete_repository(repository_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository '{repository_id}' not found",
        )


@router.get("/{repository_id}/documents", response_model=List[Document])
async def list_documents(
    repository_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    List all documents in a repository.
    """
    repo = RepositoryManager.get_repository(repository_id)
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository '{repository_id}' not found",
        )
    return RepositoryManager.list_documents(repository_id)


@router.post("/{repository_id}/upload")
async def upload_document(
    repository_id: str,
    file: UploadFile,
    current_user: User = Depends(require_role(UserRole.OPERATOR)),
):
    """
    Upload a document to a repository.
    Supports PDF, DOCX, TXT, MD files.
    """
    repo = RepositoryManager.get_repository(repository_id)
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository '{repository_id}' not found",
        )

    file_type = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    allowed_types = ["pdf", "docx", "txt", "md", "markdown"]

    if file_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{file_type}' not supported. Allowed: {allowed_types}",
        )

    repo_dir = os.path.join(REPOSITORY_STORAGE_PATH, repository_id)
    os.makedirs(repo_dir, exist_ok=True)

    file_path = os.path.join(repo_dir, file.filename)
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    doc = RepositoryManager.add_document(
        repo_id=repository_id,
        filename=file.filename,
        file_type=file_type,
        file_size=len(content),
    )

    logger.info(f"Uploaded document: {file.filename} to repository: {repository_id}")

    return {
        "success": True,
        "document": doc,
        "file_path": file_path,
        "message": "Document uploaded. Use /process endpoint to process it.",
    }


@router.post("/{repository_id}/process")
async def process_document(
    repository_id: str,
    document_id: Optional[str] = None,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Process a document using OpenDataLoader PDF and optionally Feynman.

    If document_id is provided, processes that specific document.
    Otherwise, processes all pending documents in the repository.
    """
    repo = RepositoryManager.get_repository(repository_id)
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository '{repository_id}' not found",
        )

    RepositoryManager.initialize()

    repo_dir = os.path.join(REPOSITORY_STORAGE_PATH, repository_id)

    if document_id:
        docs = [RepositoryManager.get_document(document_id)]
    else:
        docs = RepositoryManager.list_documents(repository_id)

    results = []
    for doc in docs:
        if not doc or doc.status == "processed":
            continue

        file_path = os.path.join(repo_dir, doc.filename)

        if doc.file_type == "pdf" and repo.use_opendataloader:
            try:
                from grilo_admin.services.opendataloader_service import OpenDataLoaderService

                service = OpenDataLoaderService()
                result = await service.process_pdf(
                    file_path=file_path,
                    extract_tables=repo.extract_tables,
                    extract_formulas=repo.extract_formulas,
                    enable_ocr=repo.enable_ocr,
                )

                results.append({
                    "document_id": doc.id,
                    "filename": doc.filename,
                    "success": True,
                    "markdown_length": len(result.get("markdown", "")),
                    "json_data": result.get("json_path"),
                })

            except ImportError:
                logger.warning("OpenDataLoader not available, using basic extraction")
                results.append({
                    "document_id": doc.id,
                    "filename": doc.filename,
                    "success": False,
                    "error": "OpenDataLoader not installed",
                })
        else:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            results.append({
                "document_id": doc.id,
                "filename": doc.filename,
                "success": True,
                "content_preview": content[:500],
            })

    return {
        "repository_id": repository_id,
        "documents_processed": len(results),
        "results": results,
    }


@router.post("/{repository_id}/ingest")
async def ingest_content(
    repository_id: str,
    request: IngestionRequest,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Ingest content into repository RAG index.

    Processes with Feynman (F1/F2/F3) if configured.
    """
    repo = RepositoryManager.get_repository(repository_id)
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository '{repository_id}' not found",
        )

    result = IngestionResult(
        success=True,
        chunks_created=0,
        faq_items_created=0,
        gaps_detected=0,
    )

    return result


@router.post("/{repository_id}/search")
async def search_repository(
    repository_id: str,
    request: SearchRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Search within a repository.
    """
    repo = RepositoryManager.get_repository(repository_id)
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository '{repository_id}' not found",
        )

    return SearchResult(
        query=request.query,
        results=[],
        total_results=0,
        repository_id=repository_id,
    )


@router.get("/{repository_id}/stats")
async def get_repository_stats(
    repository_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Get repository statistics.
    """
    repo = RepositoryManager.get_repository(repository_id)
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository '{repository_id}' not found",
        )

    docs = RepositoryManager.list_documents(repository_id)

    return {
        "repository_id": repository_id,
        "name": repo.name,
        "total_documents": len(docs),
        "total_chunks": repo.total_chunks,
        "status": repo.status.value,
        "documents": [
            {
                "id": d.id,
                "filename": d.filename,
                "status": d.status,
                "chunks_created": d.chunks_created,
            }
            for d in docs
        ],
    }


class FAQManager:
    """Manages FAQ items for repositories."""

    _faqs: Dict[str, Dict[str, Dict[str, Any]]] = {}
    _initialized = False

    @classmethod
    def initialize(cls):
        """Initialize storage."""
        if not cls._initialized:
            cls._initialized = True

    @classmethod
    def create_faq(
        cls,
        repository_id: str,
        question: str,
        answer: str,
        tags: Optional[List[str]] = None,
        gmif_level: str = "M3",
        confidence: float = 0.5,
        source_chunk_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new FAQ item."""
        cls.initialize()

        faq_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        faq = {
            "id": faq_id,
            "repository_id": repository_id,
            "question": question,
            "answer": answer,
            "tags": tags or [],
            "gmif_level": gmif_level,
            "confidence": confidence,
            "is_approved": False,
            "source_chunk_id": source_chunk_id,
            "created_at": now,
            "updated_at": now,
        }

        cls._faqs.setdefault(repository_id, {})[faq_id] = faq
        logger.info(f"Created FAQ: {faq_id} in repository: {repository_id}")
        return faq

    @classmethod
    def get_faq(cls, repository_id: str, faq_id: str) -> Optional[Dict[str, Any]]:
        """Get a FAQ by ID."""
        return cls._faqs.get(repository_id, {}).get(faq_id)

    @classmethod
    def list_faqs(
        cls,
        repository_id: str,
        approved_only: bool = False,
    ) -> List[Dict[str, Any]]:
        """List all FAQs in a repository."""
        faqs = cls._faqs.get(repository_id, {}).values()
        if approved_only:
            faqs = [f for f in faqs if f.get("is_approved", False)]
        return list(faqs)

    @classmethod
    def update_faq(
        cls,
        repository_id: str,
        faq_id: str,
        question: Optional[str] = None,
        answer: Optional[str] = None,
        tags: Optional[List[str]] = None,
        gmif_level: Optional[str] = None,
        confidence: Optional[float] = None,
        is_approved: Optional[bool] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update a FAQ item."""
        faq = cls._faqs.get(repository_id, {}).get(faq_id)
        if not faq:
            return None

        if question is not None:
            faq["question"] = question
        if answer is not None:
            faq["answer"] = answer
        if tags is not None:
            faq["tags"] = tags
        if gmif_level is not None:
            faq["gmif_level"] = gmif_level
        if confidence is not None:
            faq["confidence"] = confidence
        if is_approved is not None:
            faq["is_approved"] = is_approved

        faq["updated_at"] = datetime.now().isoformat()

        cls._faqs[repository_id][faq_id] = faq
        logger.info(f"Updated FAQ: {faq_id}")
        return faq

    @classmethod
    def delete_faq(cls, repository_id: str, faq_id: str) -> bool:
        """Delete a FAQ item."""
        if repository_id in cls._faqs and faq_id in cls._faqs[repository_id]:
            del cls._faqs[repository_id][faq_id]
            logger.info(f"Deleted FAQ: {faq_id}")
            return True
        return False

    @classmethod
    def approve_faq(cls, repository_id: str, faq_id: str) -> Optional[Dict[str, Any]]:
        """Approve a FAQ item."""
        faq = cls._faqs.get(repository_id, {}).get(faq_id)
        if not faq:
            return None

        faq["is_approved"] = True
        faq["updated_at"] = datetime.now().isoformat()
        return faq

    @classmethod
    def generate_from_content(
        cls,
        repository_id: str,
        content: str,
        topic: str,
    ) -> List[Dict[str, Any]]:
        """Generate FAQ items from content using Feynman F1."""
        from grilo_admin.services.feynman_processor import FeynmanProcessor

        processor = FeynmanProcessor()
        result = processor.process(content=content, topic=topic)

        if not result.f1.content:
            return []

        faqs = []

        faqs.append(cls.create_faq(
            repository_id=repository_id,
            question=f"O que é {topic}?",
            answer=result.f1.content,
            tags=["feynman-f1", "auto-generated"],
            source_chunk_id=None,
        ))

        for gap in result.f3.gaps_detected[:2]:
            clean_gap = gap.replace("Porque é que:", "").strip()
            if len(clean_gap) > 10:
                faqs.append(cls.create_faq(
                    repository_id=repository_id,
                    question=f"Porque é que {clean_gap}?",
                    answer="(Gap identificado - necessita de investigação adicional)",
                    tags=["feynman-f3", "gap-detected"],
                    source_chunk_id=None,
                ))

        logger.info(f"Generated {len(faqs)} FAQs from content for topic: {topic}")
        return faqs


@router.post("/{repository_id}/faqs", status_code=status.HTTP_201_CREATED)
async def create_faq(
    repository_id: str,
    question: str,
    answer: str,
    tags: Optional[List[str]] = None,
    gmif_level: str = "M3",
    confidence: float = 0.5,
    current_user: User = Depends(require_role(UserRole.OPERATOR)),
):
    """
    Create a new FAQ item in a repository.
    Operator or Admin can create FAQs.
    """
    repo = RepositoryManager.get_repository(repository_id)
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository '{repository_id}' not found",
        )

    faq = FAQManager.create_faq(
        repository_id=repository_id,
        question=question,
        answer=answer,
        tags=tags,
        gmif_level=gmif_level,
        confidence=confidence,
    )

    return faq


@router.get("/{repository_id}/faqs", response_model=List[Dict])
async def list_faqs(
    repository_id: str,
    approved_only: bool = False,
    current_user: User = Depends(get_current_user),
):
    """
    List all FAQ items in a repository.
    Optionally filter by approval status.
    """
    repo = RepositoryManager.get_repository(repository_id)
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository '{repository_id}' not found",
        )

    return FAQManager.list_faqs(repository_id, approved_only=approved_only)


@router.get("/{repository_id}/faqs/{faq_id}")
async def get_faq(
    repository_id: str,
    faq_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific FAQ item by ID.
    """
    faq = FAQManager.get_faq(repository_id, faq_id)
    if not faq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"FAQ '{faq_id}' not found",
        )
    return faq


@router.put("/{repository_id}/faqs/{faq_id}")
async def update_faq(
    repository_id: str,
    faq_id: str,
    question: Optional[str] = None,
    answer: Optional[str] = None,
    tags: Optional[List[str]] = None,
    gmif_level: Optional[str] = None,
    confidence: Optional[float] = None,
    is_approved: Optional[bool] = None,
    current_user: User = Depends(require_role(UserRole.OPERATOR)),
):
    """
    Update a FAQ item. Operator or Admin can update.
    """
    faq = FAQManager.update_faq(
        repository_id=repository_id,
        faq_id=faq_id,
        question=question,
        answer=answer,
        tags=tags,
        gmif_level=gmif_level,
        confidence=confidence,
        is_approved=is_approved,
    )
    if not faq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"FAQ '{faq_id}' not found",
        )
    return faq


@router.delete("/{repository_id}/faqs/{faq_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_faq(
    repository_id: str,
    faq_id: str,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Delete a FAQ item. Admin only.
    """
    deleted = FAQManager.delete_faq(repository_id, faq_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"FAQ '{faq_id}' not found",
        )


@router.post("/{repository_id}/faqs/{faq_id}/approve")
async def approve_faq(
    repository_id: str,
    faq_id: str,
    current_user: User = Depends(require_role(UserRole.OPERATOR)),
):
    """
    Approve a FAQ item for use in production.
    """
    faq = FAQManager.approve_faq(repository_id, faq_id)
    if not faq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"FAQ '{faq_id}' not found",
        )
    return faq


@router.post("/{repository_id}/faqs/generate")
async def generate_faqs_from_content(
    repository_id: str,
    content: str,
    topic: str,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Generate FAQ items from content using Feynman F1 processing.

    This processes the content through Feynman to create:
    - F1: Simple child-friendly explanation
    - F3: Why loop gaps as pending questions

    Use this to auto-generate FAQs from uploaded documents.
    """
    repo = RepositoryManager.get_repository(repository_id)
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository '{repository_id}' not found",
        )

    faqs = FAQManager.generate_from_content(
        repository_id=repository_id,
        content=content,
        topic=topic,
    )

    return {
        "repository_id": repository_id,
        "faqs_created": len(faqs),
        "faqs": faqs,
    }


@router.post("/{repository_id}/faqs/bulk")
async def create_bulk_faqs(
    repository_id: str,
    faqs: List[Dict[str, Any]],
    current_user: User = Depends(require_role(UserRole.OPERATOR)),
):
    """
    Create multiple FAQs at once.

    Each FAQ should have: question, answer, and optionally tags, gmif_level, confidence.
    """
    repo = RepositoryManager.get_repository(repository_id)
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository '{repository_id}' not found",
        )

    created = []
    for faq_data in faqs:
        faq = FAQManager.create_faq(
            repository_id=repository_id,
            question=faq_data.get("question", ""),
            answer=faq_data.get("answer", ""),
            tags=faq_data.get("tags"),
            gmif_level=faq_data.get("gmif_level", "M3"),
            confidence=faq_data.get("confidence", 0.5),
        )
        created.append(faq)

    return {
        "repository_id": repository_id,
        "faqs_created": len(created),
        "faqs": created,
    }
