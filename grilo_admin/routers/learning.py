"""
Learning Router - Auto-learning and claims management.

Provides administrative functions for:
- Auto-learning configuration
- Claims extraction and validation
- Claim queue management
- GMIF classification
"""

import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from grilo_admin.auth import get_current_user, require_role
from grilo_admin.models import User, UserRole

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/learning", tags=["learning"])


class ClaimStatus(str, Enum):
    """Claim validation status."""
    EXTRACTED = "extracted"
    PENDING = "pending"
    VALIDATING = "validating"
    VALIDATED = "validated"
    REJECTED = "rejected"
    INDEXED = "indexed"


class GMIFLevel(str, Enum):
    """GMIF classification levels."""
    M1 = "M1"  # Meta-cognitive awareness
    M2 = "M2"  # Epistemic vigilance
    M3 = "M3"  # Knowledge integration


class LearningConfig:
    """Auto-learning configuration."""

    _config: Dict[str, Any] = {
        "auto_extract_claims": True,
        "auto_index_claims": False,
        "require_approval": True,
        "min_confidence": 0.7,
        "dedup_threshold": 0.95,
        "gmif_auto_promote": False,
        "feynman_f1_enabled": True,
        "feynman_f3_enabled": True,
        "gap_trigger_threshold": 0.3,
    }

    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Get current learning configuration."""
        return cls._config.copy()

    @classmethod
    def update_config(cls, **updates) -> Dict[str, Any]:
        """Update learning configuration."""
        allowed_keys = {
            "auto_extract_claims",
            "auto_index_claims",
            "require_approval",
            "min_confidence",
            "dedup_threshold",
            "gmif_auto_promote",
            "feynman_f1_enabled",
            "feynman_f3_enabled",
            "gap_trigger_threshold",
        }
        for key, value in updates.items():
            if key in allowed_keys and value is not None:
                cls._config[key] = value
        return cls._config.copy()


class ClaimManager:
    """Manages extracted claims."""

    _claims: Dict[str, Dict[str, Any]] = {}
    _validation_queue: List[str] = []

    @classmethod
    def reset(cls):
        """Reset all claims (for testing)."""
        cls._claims = {}
        cls._validation_queue = []

    @classmethod
    def extract_claim(
        cls,
        content: str,
        source: str,
        session_id: Optional[str] = None,
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Extract a claim from content.

        Uses simple heuristics to identify factual claims:
        - Statements with subject-verb-object structure
        - Statements with modal verbs (é, foi, pode, deve)
        - Definitions and classifications
        """
        claims = []

        import re

        patterns = [
            r'([A-Z][a-z]+(?:\s+[a-z]+)*\s+(?:é|foi|são|foram|será|deve|pode)\s+[^\.!?]+)',
            r'(?:O\s+O\s+[A-Z][a-z]+\s+[a-z]+\s+é\s+[^\.!?]+)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+-\s+[^\.!?]+)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if len(match) > 20 and len(match) < 500:
                    claims.append(match.strip())

        if not claims:
            sentences = content.split('.')
            for sent in sentences:
                sent = sent.strip()
                if len(sent) > 30 and len(sent) < 400:
                    claims.append(sent)

        results = []
        for claim_text in claims[:5]:
            claim_id = str(uuid.uuid4())
            now = datetime.now().isoformat()

            confidence = min(0.9, max(0.3, len(claim_text) / 200 + 0.3))

            claim = {
                "id": claim_id,
                "content": claim_text,
                "source": source,
                "session_id": session_id,
                "context": context,
                "gmif_level": GMIFLevel.M3.value,
                "confidence": confidence,
                "status": ClaimStatus.EXTRACTED.value,
                "validation_notes": None,
                "extracted_at": now,
                "validated_at": None,
                "indexed_at": None,
            }

            cls._claims[claim_id] = claim
            cls._validation_queue.append(claim_id)
            results.append(claim)

        logger.info(f"Extracted {len(results)} claims from source: {source}")
        return results

    @classmethod
    def get_claim(cls, claim_id: str) -> Optional[Dict[str, Any]]:
        """Get a claim by ID."""
        return cls._claims.get(claim_id)

    @classmethod
    def list_claims(
        cls,
        status: Optional[ClaimStatus] = None,
        gmif_level: Optional[GMIFLevel] = None,
        min_confidence: Optional[float] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """List claims with optional filters."""
        claims = list(cls._claims.values())

        if status:
            claims = [c for c in claims if c["status"] == status.value]

        if gmif_level:
            claims = [c for c in claims if c["gmif_level"] == gmif_level.value]

        if min_confidence is not None:
            claims = [c for c in claims if c["confidence"] >= min_confidence]

        return sorted(claims, key=lambda x: x["extracted_at"], reverse=True)[:limit]

    @classmethod
    def get_pending_claims(cls, limit: int = 50) -> List[Dict[str, Any]]:
        """Get claims pending validation."""
        pending = []
        for claim_id in cls._validation_queue:
            claim = cls._claims.get(claim_id)
            if claim and claim["status"] in [ClaimStatus.EXTRACTED.value, ClaimStatus.PENDING.value]:
                pending.append(claim)
        return pending[:limit]

    @classmethod
    def validate_claim(
        cls,
        claim_id: str,
        approved: bool,
        notes: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Validate or reject a claim."""
        claim = cls._claims.get(claim_id)
        if not claim:
            return None

        if approved:
            claim["status"] = ClaimStatus.VALIDATED.value
        else:
            claim["status"] = ClaimStatus.REJECTED.value

        claim["validation_notes"] = notes
        claim["validated_at"] = datetime.now().isoformat()

        if claim_id in cls._validation_queue:
            cls._validation_queue.remove(claim_id)

        logger.info(f"Claim {claim_id}: {'validated' if approved else 'rejected'}")
        return claim

    @classmethod
    def approve_claim(cls, claim_id: str, notes: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Approve a claim (alias for validate with approved=True)."""
        return cls.validate_claim(claim_id, approved=True, notes=notes)

    @classmethod
    def reject_claim(cls, claim_id: str, notes: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Reject a claim (alias for validate with approved=False)."""
        return cls.validate_claim(claim_id, approved=False, notes=notes)

    @classmethod
    def index_claim(cls, claim_id: str) -> Optional[Dict[str, Any]]:
        """Mark a claim as indexed in RAG."""
        claim = cls._claims.get(claim_id)
        if not claim:
            return None

        if claim["status"] != ClaimStatus.VALIDATED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only validated claims can be indexed",
            )

        claim["status"] = ClaimStatus.INDEXED.value
        claim["indexed_at"] = datetime.now().isoformat()

        logger.info(f"Claim {claim_id} indexed in RAG")
        return claim

    @classmethod
    def delete_claim(cls, claim_id: str) -> bool:
        """Delete a claim."""
        if claim_id in cls._claims:
            del cls._claims[claim_id]
            if claim_id in cls._validation_queue:
                cls._validation_queue.remove(claim_id)
            return True
        return False

    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        """Get claim statistics."""
        total = len(cls._claims)
        by_status = {}
        by_gmif = {}

        for claim in cls._claims.values():
            status = claim["status"]
            gmif = claim["gmif_level"]
            by_status[status] = by_status.get(status, 0) + 1
            by_gmif[gmif] = by_gmif.get(gmif, 0) + 1

        return {
            "total_claims": total,
            "pending_validation": len(cls.get_pending_claims()),
            "by_status": by_status,
            "by_gmif_level": by_gmif,
        }


@router.get("/config")
async def get_learning_config(
    current_user: User = Depends(get_current_user),
):
    """
    Get auto-learning configuration.

    Returns the current settings for:
    - auto_extract_claims: Whether to extract claims from conversations
    - auto_index_claims: Whether to auto-index validated claims
    - require_approval: Whether to require manual approval
    - min_confidence: Minimum confidence threshold
    - dedup_threshold: Similarity threshold for deduplication
    - gmif_auto_promote: Whether to auto-promote GMIF levels
    """
    return LearningConfig.get_config()


@router.put("/config")
async def update_learning_config(
    auto_extract_claims: Optional[bool] = None,
    auto_index_claims: Optional[bool] = None,
    require_approval: Optional[bool] = None,
    min_confidence: Optional[float] = None,
    dedup_threshold: Optional[float] = None,
    gmif_auto_promote: Optional[bool] = None,
    feynman_f1_enabled: Optional[bool] = None,
    feynman_f3_enabled: Optional[bool] = None,
    gap_trigger_threshold: Optional[float] = None,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Update auto-learning configuration.

    Admin role required.
    """
    config = LearningConfig.update_config(
        auto_extract_claims=auto_extract_claims,
        auto_index_claims=auto_index_claims,
        require_approval=require_approval,
        min_confidence=min_confidence,
        dedup_threshold=dedup_threshold,
        gmif_auto_promote=gmif_auto_promote,
        feynman_f1_enabled=feynman_f1_enabled,
        feynman_f3_enabled=feynman_f3_enabled,
        gap_trigger_threshold=gap_trigger_threshold,
    )
    return config


@router.get("/stats")
async def get_learning_stats(
    current_user: User = Depends(get_current_user),
):
    """
    Get learning statistics.

    Returns:
    - Total claims extracted
    - Claims by status
    - Claims by GMIF level
    - Pending validation count
    """
    return ClaimManager.get_stats()


@router.get("/claims")
async def list_claims(
    status: Optional[str] = None,
    gmif_level: Optional[str] = None,
    min_confidence: Optional[float] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
):
    """
    List all claims.

    Query params:
    - status: Filter by status (extracted, pending, validated, rejected, indexed)
    - gmif_level: Filter by GMIF level (M1, M2, M3)
    - min_confidence: Minimum confidence threshold
    - limit: Maximum number of claims to return
    """
    claim_status = ClaimStatus(status) if status else None
    gmif = GMIFLevel(gmif_level) if gmif_level else None

    claims = ClaimManager.list_claims(
        status=claim_status,
        gmif_level=gmif,
        min_confidence=min_confidence,
        limit=limit,
    )

    return {
        "total": len(claims),
        "claims": claims,
    }


@router.get("/claims/pending")
async def get_pending_claims(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
):
    """
    Get claims pending validation.

    These are claims that need human review before being indexed.
    """
    pending = ClaimManager.get_pending_claims(limit=limit)
    return {
        "total": len(pending),
        "claims": pending,
    }


@router.get("/claims/{claim_id}")
async def get_claim(
    claim_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get a specific claim by ID."""
    claim = ClaimManager.get_claim(claim_id)
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim '{claim_id}' not found",
        )
    return claim


@router.post("/claims/{claim_id}/approve")
async def approve_claim(
    claim_id: str,
    notes: Optional[str] = None,
    current_user: User = Depends(require_role(UserRole.OPERATOR)),
):
    """
    Approve a claim for indexing.

    Operator or Admin role required.
    """
    claim = ClaimManager.approve_claim(claim_id, notes=notes)
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim '{claim_id}' not found",
        )
    return claim


@router.post("/claims/{claim_id}/reject")
async def reject_claim(
    claim_id: str,
    notes: Optional[str] = None,
    current_user: User = Depends(require_role(UserRole.OPERATOR)),
):
    """
    Reject a claim.

    Operator or Admin role required.
    """
    claim = ClaimManager.reject_claim(claim_id, notes=notes)
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim '{claim_id}' not found",
        )
    return claim


@router.post("/claims/{claim_id}/index")
async def index_claim(
    claim_id: str,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Mark a validated claim as indexed in RAG.

    Admin role required.
    Only validated claims can be indexed.
    """
    try:
        claim = ClaimManager.index_claim(claim_id)
        if not claim:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Claim '{claim_id}' not found",
            )
        return claim
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/claims/{claim_id}")
async def delete_claim(
    claim_id: str,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Delete a claim.

    Admin role required.
    """
    deleted = ClaimManager.delete_claim(claim_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim '{claim_id}' not found",
        )


@router.post("/extract")
async def extract_claims(
    content: str,
    source: str,
    session_id: Optional[str] = None,
    context: Optional[str] = None,
    current_user: User = Depends(require_role(UserRole.OPERATOR)),
):
    """
    Extract claims from content.

    This endpoint analyzes the provided content and extracts
    factual claims that can be validated and indexed.

    Operator or Admin role required.
    """
    claims = ClaimManager.extract_claim(
        content=content,
        source=source,
        session_id=session_id,
        context=context,
    )

    return {
        "extracted": len(claims),
        "claims": claims,
    }


@router.post("/process-gap")
async def process_gap(
    gap_description: str,
    topic: str,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Process a detected gap through Feynman synthesis.

    This triggers the "Ir à Escola" workflow:
    1. Generate F1 (child explanation)
    2. Generate F2 (expert explanation)
    3. Detect F3 gaps (why loop)

    Admin role required.
    """
    from grilo_admin.services.feynman_processor import FeynmanProcessor

    processor = FeynmanProcessor()
    result = processor.process(
        content=gap_description,
        topic=topic,
        include_f1=LearningConfig._config.get("feynman_f1_enabled", True),
        include_f2=True,
        include_f3=LearningConfig._config.get("feynman_f3_enabled", True),
    )

    return {
        "topic": topic,
        "f1": {
            "content": result.f1.content,
            "word_count": result.f1.word_count,
        },
        "f2": {
            "content": result.f2.content,
            "sources": result.f2.sources,
        },
        "f3": {
            "gaps_detected": result.f3.gaps_detected,
            "depth_reached": result.f3.depth_reached,
        },
        "processing_successful": result.processing_successful,
    }