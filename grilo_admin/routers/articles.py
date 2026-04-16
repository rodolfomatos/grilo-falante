"""
Articles Router - Article building and learning workflow.

Provides endpoints for:
- Article CRUD operations
- Article learning workflow (Ir à Escola)
- Shadow document management
- Gap detection and FAQ generation
- Falacia detection and propagation
- Wiki view rendering
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from grilo_admin.auth import get_current_user
from grilo_admin.models import (
    Article,
    ArticleCreate,
    ArticleUpdate,
    ArticlePhase,
    ArticleStatus,
    ArticleType,
    ArticleClaim,
    ArticleClaimCreate,
    ShadowDocument,
    ShadowDocumentCreate,
    SourceType,
    Falacia,
    FalaciaCreate,
    FalaciaType,
    FalaciaSeverity,
    FalaciaStatus,
    Gap,
    GapCreate,
    GapStatus,
    FAQFromGap,
    FAQFromGapCreate,
    ValidationStatus,
    ClaimRole,
    GMIFLevel,
    WikiView,
    LearningResult,
    ValidationQueueItem,
    User,
    UserRole,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/articles", tags=["articles"])


class ArticleManager:
    """Manages articles and their components."""

    _articles: Dict[str, Dict[str, Any]] = {}
    _claims: Dict[str, Dict[str, Any]] = {}
    _shadow_docs: Dict[str, Dict[str, Any]] = {}
    _falacias: Dict[str, Dict[str, Any]] = {}
    _gaps: Dict[str, Dict[str, Any]] = {}
    _faqs: Dict[str, Dict[str, Any]] = {}
    _initialized = False

    @classmethod
    def initialize(cls):
        """Initialize storage."""
        if not cls._initialized:
            cls._initialized = True

    @classmethod
    def create_article(cls, data: ArticleCreate, author_id: Optional[str] = None) -> Article:
        """Create a new article with associated island."""
        cls.initialize()

        article_id = str(uuid.uuid4())
        Ilha_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        article_dict = {
            "id": article_id,
            "title": data.title,
            "description": data.description or "",
            "article_type": data.article_type.value,
            "phase": ArticlePhase.EXPLORATORY.value,
            "status": ArticleStatus.DRAFT.value,
            "gmif_overall": None,
            "author_id": author_id,
            "Ilha_id": Ilha_id,
            "has_pending_validation": False,
            "has_falacias_blocking": False,
            "claims_count": 0,
            "references_count": 0,
            "shadow_docs_count": 0,
            "gaps_count": 0,
            "gaps_resolved_count": 0,
            "faqs_count": 0,
            "created_at": now,
            "updated_at": now,
            "published_at": None,
        }

        cls._articles[article_id] = article_dict

        if data.initial_content:
            cls._extract_initial_claims(article_id, data.initial_content)

        if data.topic:
            cls._create_topic_island(Ilha_id, data.topic)

        logger.info(f"Created article: {article_id} ({data.title})")
        return cls._dict_to_article(article_dict)

    @classmethod
    def _extract_initial_claims(cls, article_id: str, content: str):
        """Extract claims from initial content."""
        import re

        patterns = [
            r'([A-Z][a-z]+(?:[a-z]+)*\s+(?:é|foi|são|foram|será|deve|pode)\s+[^\.!?]+)',
            r'(?:O|A)\s+([a-z]+(?:\s+[a-z]+)*\s+(?:é|foi|são|foram)\s+[^\.!?]+)',
        ]

        claims = []
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches[:3]:
                if len(match) > 20:
                    claims.append(match.strip())

        for claim_text in claims:
            cls.create_claim(
                article_id=article_id,
                claim_text=claim_text,
                role=ClaimRole.MAIN,
            )

        cls._detect_initial_gaps(article_id, content)

    @classmethod
    def _detect_initial_gaps(cls, article_id: str, content: str):
        """Detect gaps from initial content."""
        import re

        questions = re.findall(r'([^\?]*\?)', content)
        for q in questions[:3]:
            q = q.strip()
            if len(q) > 10:
                cls.create_gap(
                    article_id=article_id,
                    question=q,
                )

    @classmethod
    def _create_topic_island(cls, Ilha_id: str, topic: str):
        """Create an island for the article topic."""
        logger.info(f"Created island: {Ilha_id} for topic: {topic}")

    @classmethod
    def create_claim(
        cls,
        article_id: str,
        claim_text: str,
        role: ClaimRole = ClaimRole.MAIN,
        gmif_level: GMIFLevel = GMIFLevel.M3,
        source_shadow_doc_id: Optional[str] = None,
    ) -> ArticleClaim:
        """Create a claim in an article."""
        claim_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        claim_dict = {
            "id": claim_id,
            "article_id": article_id,
            "claim_text": claim_text,
            "role": role.value,
            "gmif_level": gmif_level.value,
            "confidence": 0.5,
            "source_shadow_doc_id": source_shadow_doc_id,
            "validation_status": ValidationStatus.PENDING.value,
            "created_at": now,
        }

        cls._claims[claim_id] = claim_dict
        cls._update_article_counts(article_id)

        return cls._dict_to_claim(claim_dict)

    @classmethod
    def create_gap(
        cls,
        article_id: Optional[str] = None,
        question: str = "",
        Ilha_id: Optional[str] = None,
        related_claim_id: Optional[str] = None,
    ) -> Gap:
        """Create a gap (question/uncertainty)."""
        gap_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        gap_dict = {
            "id": gap_id,
            "article_id": article_id,
            "Ilha_id": Ilha_id,
            "related_claim_id": related_claim_id,
            "question": question,
            "status": GapStatus.OPEN.value,
            "resolved_by_shadow_doc_id": None,
            "propagated_to_article_id": None,
            "created_at": now,
            "updated_at": now,
        }

        cls._gaps[gap_id] = gap_dict
        cls._update_article_counts(article_id)

        cls.create_faq_from_gap(gap_id, question)

        logger.info(f"Created gap: {gap_id} - {question[:50]}...")
        return cls._dict_to_gap(gap_dict)

    @classmethod
    def create_faq_from_gap(cls, gap_id: str, question: str) -> FAQFromGap:
        """Create a FAQ from a gap (auto-generated, immediately visible)."""
        faq_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        faq_dict = {
            "id": faq_id,
            "gap_id": gap_id,
            "question": question,
            "answer": None,
            "auto_generated": True,
            "visible": True,
            "created_at": now,
            "updated_at": now,
        }

        cls._faqs[faq_id] = faq_dict

        gap = cls._gaps.get(gap_id, {})
        if gap:
            article_id = gap.get("article_id")
            if article_id and article_id in cls._articles:
                cls._articles[article_id]["faqs_count"] = cls._articles[article_id].get("faqs_count", 0) + 1

        logger.info(f"Created auto-FAQ from gap: {faq_id}")
        return cls._dict_to_faq(faq_dict)

    @classmethod
    def create_shadow_document(
        cls,
        article_id: str,
        source_name: str,
        source_type: SourceType,
        content: Optional[str] = None,
        process_with_feynman: bool = True,
    ) -> ShadowDocument:
        """Create a shadow document with Feynman processing."""
        shadow_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        feynman_f1 = None
        feynman_f2 = None
        feynman_f3_gaps = []
        extracted_claims = []

        if content and process_with_feynman:
            feynman_result = cls._process_feynman(content, source_name)
            feynman_f1 = feynman_result.get("f1")
            feynman_f2 = feynman_result.get("f2")
            feynman_f3_gaps = feynman_result.get("gaps", [])
            extracted_claims = feynman_result.get("claims", [])

        shadow_dict = {
            "id": shadow_id,
            "article_id": article_id,
            "source_name": source_name,
            "source_type": source_type.value,
            "source_reference": None,
            "source_url": None,
            "content_preview": content[:500] if content else "",
            "feynman_f1": feynman_f1,
            "feynman_f2": feynman_f2,
            "feynman_f3_gaps": feynman_f3_gaps,
            "extracted_claims": extracted_claims,
            "needs_human_validation": True,
            "validation_status": ValidationStatus.PENDING.value,
            "validated_by": None,
            "validated_at": None,
            "validation_notes": None,
            "created_at": now,
            "updated_at": now,
        }

        cls._shadow_docs[shadow_id] = shadow_dict
        cls._update_article_counts(article_id)

        for gap_question in feynman_f3_gaps:
            cls.create_gap(article_id=article_id, question=gap_question)

        logger.info(f"Created shadow doc: {shadow_id} from {source_name}")
        return cls._dict_to_shadow_doc(shadow_dict)

    @classmethod
    def _process_feynman(cls, content: str, topic: str) -> Dict[str, Any]:
        """Process content through Feynman."""
        try:
            from grilo_admin.services.feynman_processor import FeynmanProcessor
            processor = FeynmanProcessor()
            result = processor.process(content=content, topic=topic)

            return {
                "f1": result.f1.content if result.f1 else None,
                "f2": result.f2.content if result.f2 else None,
                "gaps": result.f3.gaps_detected if result.f3 else [],
                "claims": [result.f1.content] if result.f1 else [],
            }
        except Exception as e:
            logger.warning(f"Feynman processing failed: {e}")
            return {"f1": None, "f2": None, "gaps": [], "claims": []}

    @classmethod
    def get_article(cls, article_id: str) -> Optional[Article]:
        """Get article by ID."""
        article_dict = cls._articles.get(article_id)
        if article_dict:
            return cls._dict_to_article(article_dict)
        return None

    @classmethod
    def list_articles(
        cls,
        status: Optional[ArticleStatus] = None,
        phase: Optional[ArticlePhase] = None,
        author_id: Optional[str] = None,
    ) -> List[Article]:
        """List articles with filters."""
        result = []
        for article_dict in cls._articles.values():
            if status and article_dict.get("status") != status.value:
                continue
            if phase and article_dict.get("phase") != phase.value:
                continue
            if author_id and article_dict.get("author_id") != author_id:
                continue
            result.append(cls._dict_to_article(article_dict))
        return result

    @classmethod
    def update_article(cls, article_id: str, updates: ArticleUpdate) -> Optional[Article]:
        """Update an article."""
        article_dict = cls._articles.get(article_id)
        if not article_dict:
            return None

        update_data = updates.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                if hasattr(value, 'value'):
                    article_dict[key] = value.value
                else:
                    article_dict[key] = value

        article_dict["updated_at"] = datetime.now().isoformat()
        cls._articles[article_id] = article_dict

        return cls._dict_to_article(article_dict)

    @classmethod
    def get_claims_for_article(cls, article_id: str) -> List[ArticleClaim]:
        """Get all claims for an article."""
        claims = []
        for claim_dict in cls._claims.values():
            if claim_dict.get("article_id") == article_id:
                claims.append(cls._dict_to_claim(claim_dict))
        return claims

    @classmethod
    def get_shadow_docs_for_article(cls, article_id: str) -> List[ShadowDocument]:
        """Get all shadow documents for an article."""
        docs = []
        for shadow_dict in cls._shadow_docs.values():
            if shadow_dict.get("article_id") == article_id:
                docs.append(cls._dict_to_shadow_doc(shadow_dict))
        return docs

    @classmethod
    def get_gaps_for_article(cls, article_id: str) -> List[Gap]:
        """Get all gaps for an article."""
        gaps = []
        for gap_dict in cls._gaps.values():
            if gap_dict.get("article_id") == article_id:
                gaps.append(cls._dict_to_gap(gap_dict))
        return gaps

    @classmethod
    def get_faqs_for_article(cls, article_id: str) -> List[FAQFromGap]:
        """Get all FAQs for an article."""
        faqs = []
        for faq_dict in cls._faqs.values():
            gap_id = faq_dict.get("gap_id")
            gap = cls._gaps.get(gap_id, {})
            if gap.get("article_id") == article_id:
                faqs.append(cls._dict_to_faq(faq_dict))
        return faqs

    @classmethod
    def get_falacias_for_article(cls, article_id: str) -> List[Falacia]:
        """Get all falacias for an article."""
        falacias = []
        for falacia_dict in cls._falacias.values():
            if falacia_dict.get("article_id") == article_id:
                falacias.append(cls._dict_to_falacia(falacia_dict))
        return falacias

    @classmethod
    def validate_shadow_document(
        cls,
        shadow_id: str,
        approved: bool,
        validated_by: str,
        notes: Optional[str] = None,
    ) -> Optional[ShadowDocument]:
        """Validate a shadow document (curator approval)."""
        shadow_dict = cls._shadow_docs.get(shadow_id)
        if not shadow_dict:
            return None

        shadow_dict["validation_status"] = ValidationStatus.APPROVED.value if approved else ValidationStatus.REJECTED.value
        shadow_dict["validated_by"] = validated_by
        shadow_dict["validated_at"] = datetime.now().isoformat()
        shadow_dict["validation_notes"] = notes
        shadow_dict["updated_at"] = datetime.now().isoformat()

        article_id = shadow_dict.get("article_id")
        if article_id and article_id in cls._articles:
            cls._articles[article_id]["has_pending_validation"] = cls._has_pending_validation(article_id)

        if approved:
            for claim_text in shadow_dict.get("extracted_claims", []):
                cls.create_claim(
                    article_id=article_id,
                    claim_text=claim_text,
                    role=ClaimRole.REFERENCE,
                    source_shadow_doc_id=shadow_id,
                )

            gap_id = shadow_dict.get("feynman_f3_gaps", [None])[0]
            if gap_id:
                cls.resolve_gap(gap_id, shadow_id)

        logger.info(f"Shadow doc {shadow_id}: {'APPROVED' if approved else 'REJECTED'} by {validated_by}")
        return cls._dict_to_shadow_doc(shadow_dict)

    @classmethod
    def resolve_gap(cls, gap_id: str, resolved_by_shadow_doc_id: str) -> Optional[Gap]:
        """Mark a gap as resolved."""
        gap_dict = cls._gaps.get(gap_id)
        if not gap_dict:
            return None

        gap_dict["status"] = GapStatus.RESOLVED.value
        gap_dict["resolved_by_shadow_doc_id"] = resolved_by_shadow_doc_id
        gap_dict["updated_at"] = datetime.now().isoformat()

        article_id = gap_dict.get("article_id")
        if article_id and article_id in cls._articles:
            cls._articles[article_id]["gaps_resolved_count"] = cls._articles[article_id].get("gaps_resolved_count", 0) + 1

        return cls._dict_to_gap(gap_dict)

    @classmethod
    def _has_pending_validation(cls, article_id: str) -> bool:
        """Check if article has pending validations."""
        for shadow_dict in cls._shadow_docs.values():
            if shadow_dict.get("article_id") == article_id:
                if shadow_dict.get("validation_status") == ValidationStatus.PENDING.value:
                    return True
        return False

    @classmethod
    def _update_article_counts(cls, article_id: str):
        """Update article counts."""
        if article_id not in cls._articles:
            return

        article = cls._articles[article_id]
        article["claims_count"] = sum(1 for c in cls._claims.values() if c.get("article_id") == article_id)
        article["shadow_docs_count"] = sum(1 for s in cls._shadow_docs.values() if s.get("article_id") == article_id)
        article["gaps_count"] = sum(1 for g in cls._gaps.values() if g.get("article_id") == article_id)

    @classmethod
    def get_wiki_view(cls, article_id: str) -> Optional[WikiView]:
        """Get complete wiki view for an article."""
        article = cls.get_article(article_id)
        if not article:
            return None

        claims = cls.get_claims_for_article(article_id)
        shadow_docs = cls.get_shadow_docs_for_article(article_id)
        gaps = cls.get_gaps_for_article(article_id)
        faqs = cls.get_faqs_for_article(article_id)
        falacias = cls.get_falacias_for_article(article_id)

        gmif_summary = {"M1": 0, "M2": 0, "M3": 0, "M4": 0, "M5": 0, "M6": 0, "M7": 0, "M8": 0}
        for claim in claims:
            gmif_summary[claim.gmif_level.value] = gmif_summary.get(claim.gmif_level.value, 0) + 1

        claims_tree = {
            "sections": [
                {
                    "title": "Claims",
                    "claims": [
                        {
                            "id": c.id,
                            "text": c.claim_text,
                            "gmif": c.gmif_level.value,
                            "role": c.role.value,
                            "status": c.validation_status.value,
                        }
                        for c in claims
                    ],
                }
            ]
        }

        logical_links = [
            {
                "from": c1.id,
                "to": c2.id,
                "type": "SUPPORTS" if i % 2 == 0 else "RELATED",
            }
            for i, (c1, c2) in enumerate(zip(claims, claims[1:]))
        ]

        return WikiView(
            article=article,
            claims_tree=claims_tree,
            logical_links=logical_links,
            shadow_documents=shadow_docs,
            gaps=gaps,
            faqs=faqs,
            falacias=falacias,
            gmif_summary=gmif_summary,
        )

    @classmethod
    def _dict_to_article(cls, d: Dict[str, Any]) -> Article:
        """Convert dict to Article."""
        return Article(
            id=d["id"],
            title=d["title"],
            description=d.get("description", ""),
            article_type=ArticleType(d.get("article_type", "scientific")),
            phase=ArticlePhase(d.get("phase", "exploratory")),
            status=ArticleStatus(d.get("status", "draft")),
            gmif_overall=d.get("gmif_overall"),
            author_id=d.get("author_id"),
            Ilha_id=d.get("Ilha_id"),
            has_pending_validation=d.get("has_pending_validation", False),
            has_falacias_blocking=d.get("has_falacias_blocking", False),
            claims_count=d.get("claims_count", 0),
            references_count=d.get("references_count", 0),
            shadow_docs_count=d.get("shadow_docs_count", 0),
            gaps_count=d.get("gaps_count", 0),
            gaps_resolved_count=d.get("gaps_resolved_count", 0),
            faqs_count=d.get("faqs_count", 0),
            created_at=datetime.fromisoformat(d["created_at"]) if isinstance(d["created_at"], str) else d["created_at"],
            updated_at=datetime.fromisoformat(d["updated_at"]) if isinstance(d["updated_at"], str) else d["updated_at"],
            published_at=datetime.fromisoformat(d["published_at"]) if d.get("published_at") else None,
        )

    @classmethod
    def _dict_to_claim(cls, d: Dict[str, Any]) -> ArticleClaim:
        """Convert dict to ArticleClaim."""
        return ArticleClaim(
            id=d["id"],
            article_id=d["article_id"],
            claim_text=d["claim_text"],
            role=ClaimRole(d.get("role", "main")),
            gmif_level=GMIFLevel(d.get("gmif_level", "M3")),
            confidence=d.get("confidence", 0.5),
            source_shadow_doc_id=d.get("source_shadow_doc_id"),
            validation_status=ValidationStatus(d.get("validation_status", "pending")),
            created_at=datetime.fromisoformat(d["created_at"]) if isinstance(d["created_at"], str) else d["created_at"],
        )

    @classmethod
    def _dict_to_shadow_doc(cls, d: Dict[str, Any]) -> ShadowDocument:
        """Convert dict to ShadowDocument."""
        return ShadowDocument(
            id=d["id"],
            article_id=d["article_id"],
            source_name=d["source_name"],
            source_type=SourceType(d.get("source_type", "upload")),
            source_reference=d.get("source_reference"),
            source_url=d.get("source_url"),
            content_preview=d.get("content_preview", ""),
            feynman_f1=d.get("feynman_f1"),
            feynman_f2=d.get("feynman_f2"),
            feynman_f3_gaps=d.get("feynman_f3_gaps", []),
            extracted_claims=d.get("extracted_claims", []),
            needs_human_validation=d.get("needs_human_validation", True),
            validation_status=ValidationStatus(d.get("validation_status", "pending")),
            validated_by=d.get("validated_by"),
            validated_at=datetime.fromisoformat(d["validated_at"]) if d.get("validated_at") else None,
            validation_notes=d.get("validation_notes"),
            created_at=datetime.fromisoformat(d["created_at"]) if isinstance(d["created_at"], str) else d["created_at"],
            updated_at=datetime.fromisoformat(d["updated_at"]) if isinstance(d["updated_at"], str) else d["updated_at"],
        )

    @classmethod
    def _dict_to_gap(cls, d: Dict[str, Any]) -> Gap:
        """Convert dict to Gap."""
        return Gap(
            id=d["id"],
            article_id=d.get("article_id"),
            Ilha_id=d.get("Ilha_id"),
            related_claim_id=d.get("related_claim_id"),
            question=d["question"],
            status=GapStatus(d.get("status", "open")),
            resolved_by_shadow_doc_id=d.get("resolved_by_shadow_doc_id"),
            propagated_to_article_id=d.get("propagated_to_article_id"),
            created_at=datetime.fromisoformat(d["created_at"]) if isinstance(d["created_at"], str) else d["created_at"],
            updated_at=datetime.fromisoformat(d["updated_at"]) if isinstance(d["updated_at"], str) else d["updated_at"],
        )

    @classmethod
    def _dict_to_faq(cls, d: Dict[str, Any]) -> FAQFromGap:
        """Convert dict to FAQFromGap."""
        return FAQFromGap(
            id=d["id"],
            gap_id=d["gap_id"],
            question=d["question"],
            answer=d.get("answer"),
            auto_generated=d.get("auto_generated", True),
            visible=d.get("visible", True),
            created_at=datetime.fromisoformat(d["created_at"]) if isinstance(d["created_at"], str) else d["created_at"],
            updated_at=datetime.fromisoformat(d["updated_at"]) if isinstance(d["updated_at"], str) else d["updated_at"],
        )

    @classmethod
    def _dict_to_falacia(cls, d: Dict[str, Any]) -> Falacia:
        """Convert dict to Falacia."""
        return Falacia(
            id=d["id"],
            article_id=d["article_id"],
            claim_1_id=d.get("claim_1_id"),
            claim_2_id=d.get("claim_2_id"),
            falacia_type=FalaciaType(d.get("falacia_type", "unknown")),
            severity=FalaciaSeverity(d.get("severity", "warning")),
            description=d.get("description", ""),
            status=FalaciaStatus(d.get("status", "detected")),
            propagated=d.get("propagated", False),
            affected_ilhas=d.get("affected_ilhas", []),
            correction_suggestion=d.get("correction_suggestion"),
            created_at=datetime.fromisoformat(d["created_at"]) if isinstance(d["created_at"], str) else d["created_at"],
            updated_at=datetime.fromisoformat(d["updated_at"]) if isinstance(d["updated_at"], str) else d["updated_at"],
        )

    @classmethod
    def create_falacia(cls, falacia_create: FalaciaCreate) -> Falacia:
        """Create a new falacia."""
        falacia_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        falacia_dict = {
            "id": falacia_id,
            "article_id": falacia_create.article_id,
            "claim_1_id": falacia_create.claim_1_id,
            "claim_2_id": falacia_create.claim_2_id,
            "falacia_type": falacia_create.falacia_type.value,
            "severity": falacia_create.severity.value,
            "description": falacia_create.description,
            "status": FalaciaStatus.DETECTED.value,
            "propagated": False,
            "affected_ilhas": [],
            "correction_suggestion": None,
            "created_at": now,
            "updated_at": now,
        }

        cls._falacias[falacia_id] = falacia_dict

        if falacia_create.severity == FalaciaSeverity.BLOCKING:
            article_dict = cls._articles.get(falacia_create.article_id)
            if article_dict:
                article_dict["has_falacias_blocking"] = True

        logger.info(f"Created falacia: {falacia_id} ({falacia_create.falacia_type.value})")
        return cls._dict_to_falacia(falacia_dict)

    @classmethod
    def get_falacia(cls, falacia_id: str) -> Optional[Falacia]:
        """Get a falacia by ID."""
        falacia_dict = cls._falacias.get(falacia_id)
        if falacia_dict:
            return cls._dict_to_falacia(falacia_dict)
        return None

    @classmethod
    def get_claim(cls, claim_id: str) -> Optional[ArticleClaim]:
        """Get a claim by ID."""
        claim_dict = cls._claims.get(claim_id)
        if claim_dict:
            return cls._dict_to_claim(claim_dict)
        return None

    @classmethod
    def update_falacia(cls, falacia_id: str, updates: Dict[str, Any]) -> Optional[Falacia]:
        """Update a falacia."""
        falacia_dict = cls._falacias.get(falacia_id)
        if not falacia_dict:
            return None

        for key, value in updates.items():
            if value is not None:
                falacia_dict[key] = value

        falacia_dict["updated_at"] = datetime.now().isoformat()
        cls._falacias[falacia_id] = falacia_dict

        return cls._dict_to_falacia(falacia_dict)


@router.post("", response_model=Article, status_code=status.HTTP_201_CREATED)
async def create_article(
    data: ArticleCreate,
    current_user: User = Depends(get_current_user),
):
    """
    Create a new article.

    Creates an article in EXPLORATORY phase with:
    - Initial claims extracted from content (if provided)
    - Gaps identified from questions
    - FAQs auto-generated from gaps
    - Associated island for topic
    """
    return ArticleManager.create_article(data, author_id=current_user.id)


@router.get("", response_model=List[Article])
async def list_articles(
    status: Optional[str] = None,
    phase: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """
    List all articles.

    Filters:
    - status: draft, pending_validation, published, archived
    - phase: exploratory, learning, writing, review
    """
    status_enum = ArticleStatus(status) if status else None
    phase_enum = ArticlePhase(phase) if phase else None
    return ArticleManager.list_articles(status=status_enum, phase=phase_enum)


@router.get("/{article_id}", response_model=Article)
async def get_article(
    article_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get article by ID."""
    article = ArticleManager.get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail=f"Article '{article_id}' not found")
    return article


@router.put("/{article_id}", response_model=Article)
async def update_article(
    article_id: str,
    updates: ArticleUpdate,
    current_user: User = Depends(get_current_user),
):
    """Update an article."""
    article = ArticleManager.update_article(article_id, updates)
    if not article:
        raise HTTPException(status_code=404, detail=f"Article '{article_id}' not found")
    return article


@router.post("/{article_id}/learn")
async def learn_article(
    article_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Trigger learning workflow for an article.

    This performs "Ir à Escola" for each open gap:
    - Creates shadow documents from sources
    - Processes with Feynman F1/F2/F3
    - Auto-generates FAQs from gaps
    """
    article = ArticleManager.get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail=f"Article '{article_id}' not found")

    gaps = ArticleManager.get_gaps_for_article(article_id)
    shadow_docs_created = 0
    claims_extracted = 0
    faqs_auto_generated = 0
    errors = []

    for gap in gaps:
        if gap.status != GapStatus.OPEN:
            continue

        try:
            content = f"Research about: {gap.question}"
            shadow = ArticleManager.create_shadow_document(
                article_id=article_id,
                source_name=f"Research for: {gap.question[:50]}",
                source_type=SourceType.INTERNAL,
                content=content,
                process_with_feynman=True,
            )
            shadow_docs_created += 1
            claims_extracted += len(shadow.extracted_claims)
            faqs_auto_generated += len(shadow.feynman_f3_gaps)

        except Exception as e:
            errors.append(f"Gap {gap.id}: {str(e)}")

    ArticleManager.update_article(article_id, ArticleUpdate(phase=ArticlePhase.LEARNING))

    return LearningResult(
        success=len(errors) == 0,
        gaps_found=len(gaps),
        shadow_docs_created=shadow_docs_created,
        claims_extracted=claims_extracted,
        faqs_auto_generated=faqs_auto_generated,
        errors=errors,
    )


@router.get("/{article_id}/claims", response_model=List[ArticleClaim])
async def get_article_claims(
    article_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get all claims for an article."""
    article = ArticleManager.get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail=f"Article '{article_id}' not found")
    return ArticleManager.get_claims_for_article(article_id)


@router.post("/{article_id}/claims", response_model=ArticleClaim, status_code=status.HTTP_201_CREATED)
async def create_article_claim(
    article_id: str,
    claim_text: str,
    role: ClaimRole = ClaimRole.MAIN,
    current_user: User = Depends(get_current_user),
):
    """Add a claim to an article."""
    article = ArticleManager.get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail=f"Article '{article_id}' not found")
    return ArticleManager.create_claim(
        article_id=article_id,
        claim_text=claim_text,
        role=role,
    )


@router.get("/{article_id}/shadow-documents", response_model=List[ShadowDocument])
async def get_shadow_documents(
    article_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get all shadow documents for an article."""
    article = ArticleManager.get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail=f"Article '{article_id}' not found")
    return ArticleManager.get_shadow_docs_for_article(article_id)


@router.post("/{article_id}/shadow-documents", response_model=ShadowDocument, status_code=status.HTTP_201_CREATED)
async def create_shadow_document(
    article_id: str,
    source_name: str,
    source_type: SourceType,
    content: Optional[str] = None,
    process_with_feynman: bool = True,
    current_user: User = Depends(get_current_user),
):
    """Create a shadow document for an article."""
    article = ArticleManager.get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail=f"Article '{article_id}' not found")
    return ArticleManager.create_shadow_document(
        article_id=article_id,
        source_name=source_name,
        source_type=source_type,
        content=content,
        process_with_feynman=process_with_feynman,
    )


@router.post("/shadow-documents/{shadow_id}/validate")
async def validate_shadow_document(
    shadow_id: str,
    approved: bool,
    notes: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """
    Validate a shadow document (curator approval).

    All shadow documents require human validation before being considered
    authoritative for scientific articles.
    """
    shadow = ArticleManager.validate_shadow_document(
        shadow_id=shadow_id,
        approved=approved,
        validated_by=current_user.id,
        notes=notes,
    )
    if not shadow:
        raise HTTPException(status_code=404, detail=f"Shadow doc '{shadow_id}' not found")
    return shadow


@router.get("/{article_id}/gaps", response_model=List[Gap])
async def get_article_gaps(
    article_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get all gaps for an article."""
    article = ArticleManager.get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail=f"Article '{article_id}' not found")
    return ArticleManager.get_gaps_for_article(article_id)


@router.get("/{article_id}/faqs", response_model=List[FAQFromGap])
async def get_article_faqs(
    article_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get all auto-generated FAQs for an article."""
    article = ArticleManager.get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail=f"Article '{article_id}' not found")
    return ArticleManager.get_faqs_for_article(article_id)


@router.get("/{article_id}/wiki")
async def get_article_wiki(
    article_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Get complete wiki view for an article.

    Returns the full article structure suitable for wiki rendering:
    - Article metadata
    - Claims tree with GMIF levels
    - Logical links between claims
    - Shadow documents
    - Gaps and FAQs
    - Falácias detected
    - GMIF summary
    """
    wiki = ArticleManager.get_wiki_view(article_id)
    if not wiki:
        raise HTTPException(status_code=404, detail=f"Article '{article_id}' not found")
    return wiki


@router.post("/{article_id}/detect-falacias")
async def detect_falacias(
    article_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Detect fallacies in an article's claims.

    Uses pattern matching and heuristics to identify:
    - Contradictions
    - Generalizations
    - Appeal to authority
    - Appeal to majority
    - Causal fallacies
    - And more

    Returns detected fallacies and propagates to other articles.
    """
    article = ArticleManager.get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail=f"Article '{article_id}' not found")

    from grilo_admin.services.falacia_service import FalaciaDetector, FalaciaPropagator

    claims = ArticleManager.get_claims_for_article(article_id)
    if not claims:
        return {"detected": 0, "falacias": [], "message": "No claims to analyze"}

    detected = FalaciaDetector.detect_falacias(claims)

    for falacia_create in detected:
        ArticleManager.create_falacia(falacia_create)

    propagator = FalaciaPropagator()
    all_claims = {article_id: claims}

    for other_article in ArticleManager.list_articles():
        if other_article.id != article_id:
            other_claims = ArticleManager.get_claims_for_article(other_article.id)
            if other_claims:
                all_claims[other_article.id] = other_claims

    propagation_results = []
    for i, falacia_create in enumerate(detected):
        if i < len(ArticleManager._falacias):
            falacia_id = list(ArticleManager._falacias.keys())[i]
            result = propagator.propagate(
                falacia_id=falacia_id,
                claim_ids=[falacia_create.claim_1_id, falacia_create.claim_2_id],
                article_id=article_id,
                all_articles_claims=all_claims,
            )
            propagation_results.append(result)

    blocking_count = sum(1 for f in detected if f.severity == FalaciaSeverity.BLOCKING)

    return {
        "detected": len(detected),
        "falacias": detected,
        "blocking_count": blocking_count,
        "propagation_results": propagation_results,
    }


@router.get("/{article_id}/falacias", response_model=List[Falacia])
async def get_article_falacias(
    article_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get all detected fallacies for an article."""
    article = ArticleManager.get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail=f"Article '{article_id}' not found")
    return ArticleManager.get_falacias_for_article(article_id)


@router.post("/falacias/{falacia_id}/correct")
async def correct_falacia(
    falacia_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Get correction suggestion for a falacia.

    Returns:
    - Suggested correction approach
    - Corrected claim text (if applicable)
    """
    falacia = ArticleManager.get_falacia(falacia_id)
    if not falacia:
        raise HTTPException(status_code=404, detail=f"Falacia '{falacia_id}' not found")

    from grilo_admin.services.falacia_service import FalaciaCorrector

    suggestion = FalaciaCorrector.suggest_correction(falacia.falacia_type)

    corrected_claim = None
    if falacia.claim_1_id:
        claim = ArticleManager.get_claim(falacia.claim_1_id)
        if claim:
            corrected_claim = FalaciaCorrector.generate_corrected_claim(
                claim.claim_text, falacia.falacia_type
            )

    ArticleManager.update_falacia(falacia_id, {
        "status": FalaciaStatus.CORRECTED.value,
        "correction_suggestion": suggestion,
    })

    return {
        "falacia_id": falacia_id,
        "suggestion": suggestion,
        "corrected_claim": corrected_claim,
    }


@router.post("/falacias/{falacia_id}/signal")
async def signal_falacia(
    falacia_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Signal a falacia recursively to all affected items.

    This marks the falacia as SIGNORED and propagates
    notifications to all affected islands and owners.
    """
    falacia = ArticleManager.get_falacia(falacia_id)
    if not falacia:
        raise HTTPException(status_code=404, detail=f"Falacia '{falacia_id}' not found")

    from grilo_admin.services.falacia_service import FalaciaPropagator

    all_claims = {}
    for article in ArticleManager.list_articles():
        claims = ArticleManager.get_claims_for_article(article.id)
        if claims:
            all_claims[article.id] = claims

    propagator = FalaciaPropagator()
    result = propagator.propagate(
        falacia_id=falacia_id,
        claim_ids=[falacia.claim_1_id, falacia.claim_2_id] if falacia.claim_1_id else [falacia.claim_2_id],
        article_id=falacia.article_id,
        all_articles_claims=all_claims,
    )

    ArticleManager.update_falacia(falacia_id, {
        "status": FalaciaStatus.SIGNALED.value,
        "propagated": True,
        "affected_ilhas": result.get("affected_ilhas", []),
    })

    return {
        "falacia_id": falacia_id,
        "signaled": True,
        "affected_items": result,
        "message": f"Falacia propagated to {result.get('total_affected', 0)} items",
    }


@router.get("/validation-queue")
async def get_validation_queue(
    current_user: User = Depends(get_current_user),
):
    """Get all shadow documents pending validation."""
    queue = []
    for shadow_dict in ArticleManager._shadow_docs.values():
        if shadow_dict.get("validation_status") == ValidationStatus.PENDING.value:
            article = ArticleManager.get_article(shadow_dict["article_id"])
            queue.append(ValidationQueueItem(
                id=shadow_dict["id"],
                type="shadow_document",
                shadow_doc_id=shadow_dict["id"],
                article_id=shadow_dict["article_id"],
                article_title=article.title if article else "Unknown",
                source_name=shadow_dict["source_name"],
                source_type=SourceType(shadow_dict.get("source_type", "upload")),
                created_at=datetime.fromisoformat(shadow_dict["created_at"]) if isinstance(shadow_dict["created_at"], str) else shadow_dict["created_at"],
            ))
    return {"total": len(queue), "items": queue}