"""
Article Models - Article, ShadowDocument, Falacia, Gap, FAQ

These models support the article building workflow:
1. Articles are built from claims with GMIF classification
2. ShadowDocuments are Feynman-processed interpretations of sources
3. Falacias are logical fallacies detected between claims
4. Gaps are questions/uncertainties that trigger learning
5. FAQs are auto-generated from gaps
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ArticlePhase(str, Enum):
    """Article building phase."""
    EXPLORATORY = "exploratory"
    LEARNING = "learning"
    WRITING = "writing"
    REVIEW = "review"


class ArticleStatus(str, Enum):
    """Article status."""
    DRAFT = "draft"
    PENDING_VALIDATION = "pending_validation"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ArticleType(str, Enum):
    """Type of article."""
    SCIENTIFIC = "scientific"
    ESSAY = "essay"
    REPORT = "report"
    FAQ = "faq"
    OTHER = "other"


class SourceType(str, Enum):
    """Type of source for shadow document."""
    UPLOAD = "upload"
    WEB = "web"
    INTERNAL = "internal"


class FalaciaType(str, Enum):
    """Types of logical fallacies."""
    CONTRADICTION = "contradiction"
    GENERALIZATION = "generalization"
    APPEAL_TO_AUTHORITY = "appeal_to_authority"
    APPEAL_TO_MAJORITY = "appeal_to_majority"
    CAUSAL_FALLACY = "causal_fallacy"
    STRAWMAN = "strawman"
    FALSE_DILEMMA = "false_dilemma"
    CIRCULAR_REASONING = "circular_reasoning"
    UNKNOWN = "unknown"


class FalaciaSeverity(str, Enum):
    """Severity of fallacy."""
    WARNING = "warning"
    BLOCKING = "blocking"


class FalaciaStatus(str, Enum):
    """Status of detected fallacy."""
    DETECTED = "detected"
    VISIBLE = "visible"
    CORRECTED = "corrected"
    SIGNALED = "signaled"


class GapStatus(str, Enum):
    """Status of a gap."""
    OPEN = "open"
    RESOLVED = "resolved"
    PROPAGATED = "propagated"


class ValidationStatus(str, Enum):
    """Validation status for claims and shadow docs."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ClaimRole(str, Enum):
    """Role of a claim in an article."""
    MAIN = "main"
    CONTEXT = "context"
    REFERENCE = "reference"


class GMIFLevel(str, Enum):
    """GMIF epistemic confidence levels."""
    M1 = "M1"
    M2 = "M2"
    M3 = "M3"
    M4 = "M4"
    M5 = "M5"
    M6 = "M6"
    M7 = "M7"
    M8 = "M8"


class ArticleBase(BaseModel):
    """Base article properties."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = ""
    article_type: ArticleType = ArticleType.SCIENTIFIC


class ArticleCreate(ArticleBase):
    """Article creation request."""
    topic: Optional[str] = None
    initial_content: Optional[str] = None


class ArticleUpdate(BaseModel):
    """Article update request."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    article_type: Optional[ArticleType] = None
    phase: Optional[ArticlePhase] = None
    status: Optional[ArticleStatus] = None


class ArticleInDB(ArticleBase):
    """Article as stored in database."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    phase: ArticlePhase = ArticlePhase.EXPLORATORY
    status: ArticleStatus = ArticleStatus.DRAFT
    gmif_overall: Optional[str] = None

    author_id: Optional[str] = None
    Ilha_id: Optional[str] = None

    has_pending_validation: bool = False
    has_falacias_blocking: bool = False

    claims_count: int = 0
    references_count: int = 0
    shadow_docs_count: int = 0
    gaps_count: int = 0
    gaps_resolved_count: int = 0
    faqs_count: int = 0

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    published_at: Optional[datetime] = None


class Article(ArticleBase):
    """Article as returned by API."""
    id: str
    phase: ArticlePhase
    status: ArticleStatus
    gmif_overall: Optional[str] = None
    author_id: Optional[str] = None
    Ilha_id: Optional[str] = None
    has_pending_validation: bool
    has_falacias_blocking: bool
    claims_count: int
    references_count: int
    shadow_docs_count: int
    gaps_count: int
    gaps_resolved_count: int
    faqs_count: int
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ShadowDocumentBase(BaseModel):
    """Base shadow document properties.

    DEPRECATED: Use ShadowDocument from grilo_admin.models.ilha instead.
    This base class is kept for backward compatibility.
    """
    source_name: str
    source_type: SourceType
    source_reference: Optional[str] = None
    source_url: Optional[str] = None


class ShadowDocumentCreate(ShadowDocumentBase):
    """Shadow document creation request.

    DEPRECATED: Use ShadowDocument from grilo_admin.models.ilha instead.
    """
    article_id: str
    content: Optional[str] = None
    process_with_feynman: bool = True


class ShadowDocumentInDB(BaseModel):
    """Shadow document as stored in database.

    DEPRECATED: Use ShadowDocument from grilo_admin.models.ilha instead.
    This class is kept for backward compatibility with article workflow.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    article_id: str

    # Shadow document content from ILHA model
    source_name: str
    source_type: SourceType
    source_reference: Optional[str] = None
    source_url: Optional[str] = None

    content_preview: str = ""

    # Feynman layers (aligned with ILHA ShadowDocument)
    feynman_f1: Optional[str] = None
    feynman_f2: Optional[str] = None
    feynman_f3_gaps: List[str] = Field(default_factory=list)

    # Extracted claims (aligned with ILHA ShadowDocument)
    extracted_claims: List[str] = Field(default_factory=list)

    # Additional epistemic metadata (aligned with ILHA ShadowDocument)
    evidence_level: str = "weak"
    assumptions: List[str] = Field(default_factory=list)
    misuse_risks: List[str] = Field(default_factory=list)

    # Article-specific validation
    needs_human_validation: bool = True
    validation_status: ValidationStatus = ValidationStatus.PENDING
    validated_by: Optional[str] = None
    validated_at: Optional[datetime] = None
    validation_notes: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def to_ilha_shadow_document(self) -> "ShadowDocument":
        """Convert to ILHA ShadowDocument for unified storage."""
        from grilo_admin.models.ilha import ShadowDocument
        return ShadowDocument(
            id=self.id,
            source_name=self.source_name,
            source_type=self.source_type.value if hasattr(self.source_type, 'value') else self.source_type,
            source_reference=self.source_reference,
            feynman_f1=self.feynman_f1,
            feynman_f2=self.feynman_f2,
            feynman_f3_gaps=self.feynman_f3_gaps,
            extracted_claims=self.extracted_claims,
            evidence_level=self.evidence_level,
            assumptions=self.assumptions,
            misuse_risks=self.misuse_risks,
            created_at=self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
        )


class ShadowDocument(BaseModel):
    """Shadow document as returned by API.

    DEPRECATED: Use ShadowDocument from grilo_admin.models.ilha instead.
    This class is kept for backward compatibility with article workflow.
    """
    id: str
    article_id: str
    source_name: str
    source_type: str
    source_reference: Optional[str] = None
    source_url: Optional[str] = None
    content_preview: str
    feynman_f1: Optional[str] = None
    feynman_f2: Optional[str] = None
    feynman_f3_gaps: List[str]
    extracted_claims: List[str]
    evidence_level: str = "weak"
    assumptions: List[str] = Field(default_factory=list)
    misuse_risks: List[str] = Field(default_factory=list)
    needs_human_validation: bool
    validation_status: str
    validated_by: Optional[str] = None
    validated_at: Optional[str] = None
    validation_notes: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class ArticleClaimBase(BaseModel):
    """Base article claim properties."""
    claim_text: str
    role: ClaimRole = ClaimRole.MAIN


class ArticleClaimCreate(ArticleClaimBase):
    """Article claim creation request."""
    article_id: str
    gmif_level: Optional[GMIFLevel] = GMIFLevel.M3
    source_shadow_doc_id: Optional[str] = None


class ArticleClaimInDB(ArticleClaimBase):
    """Article claim as stored in database."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    article_id: str
    gmif_level: GMIFLevel = GMIFLevel.M3
    confidence: float = 0.5
    source_shadow_doc_id: Optional[str] = None
    validation_status: ValidationStatus = ValidationStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)


class ArticleClaim(ArticleClaimBase):
    """Article claim as returned by API."""
    id: str
    article_id: str
    gmif_level: GMIFLevel
    confidence: float
    source_shadow_doc_id: Optional[str] = None
    validation_status: ValidationStatus
    created_at: datetime

    class Config:
        from_attributes = True


class FalaciaBase(BaseModel):
    """Base falacia properties."""
    falacia_type: FalaciaType
    severity: FalaciaSeverity = FalaciaSeverity.WARNING
    description: str


class FalaciaCreate(FalaciaBase):
    """Falacia creation request."""
    article_id: str
    claim_1_id: Optional[str] = None
    claim_2_id: Optional[str] = None


class FalaciaInDB(FalaciaBase):
    """Falacia as stored in database."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    article_id: str
    claim_1_id: Optional[str] = None
    claim_2_id: Optional[str] = None
    status: FalaciaStatus = FalaciaStatus.DETECTED
    propagated: bool = False
    affected_ilhas: List[str] = Field(default_factory=list)
    correction_suggestion: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Falacia(FalaciaBase):
    """Falacia as returned by API."""
    id: str
    article_id: str
    claim_1_id: Optional[str] = None
    claim_2_id: Optional[str] = None
    status: FalaciaStatus
    propagated: bool
    affected_ilhas: List[str]
    correction_suggestion: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GapBase(BaseModel):
    """Base gap properties."""
    question: str


class GapCreate(GapBase):
    """Gap creation request."""
    article_id: Optional[str] = None
    Ilha_id: Optional[str] = None
    related_claim_id: Optional[str] = None


class GapInDB(GapBase):
    """Gap as stored in database."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    article_id: Optional[str] = None
    Ilha_id: Optional[str] = None
    related_claim_id: Optional[str] = None
    status: GapStatus = GapStatus.OPEN
    resolved_by_shadow_doc_id: Optional[str] = None
    propagated_to_article_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Gap(GapBase):
    """Gap as returned by API."""
    id: str
    article_id: Optional[str] = None
    Ilha_id: Optional[str] = None
    related_claim_id: Optional[str] = None
    status: GapStatus
    resolved_by_shadow_doc_id: Optional[str] = None
    propagated_to_article_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FAQFromGapBase(BaseModel):
    """Base FAQ from gap properties."""
    question: str


class FAQFromGapCreate(FAQFromGapBase):
    """FAQ from gap creation request."""
    gap_id: str
    answer: Optional[str] = None


class FAQFromGapInDB(FAQFromGapBase):
    """FAQ from gap as stored in database."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    gap_id: str
    answer: Optional[str] = None
    auto_generated: bool = True
    visible: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class FAQFromGap(FAQFromGapBase):
    """FAQ from gap as returned by API."""
    id: str
    gap_id: str
    answer: Optional[str] = None
    auto_generated: bool
    visible: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WikiView(BaseModel):
    """Complete wiki view structure for an article."""
    article: Article
    claims_tree: Dict[str, Any]
    logical_links: List[Dict[str, Any]]
    shadow_documents: List[ShadowDocument]
    gaps: List[Gap]
    faqs: List[FAQFromGap]
    falacias: List[Falacia]
    gmif_summary: Dict[str, int]


class LearningResult(BaseModel):
    """Result from a learning/Ir à Escola operation."""
    success: bool
    gaps_found: int
    shadow_docs_created: int
    claims_extracted: int
    faqs_auto_generated: int
    errors: List[str] = Field(default_factory=list)


class ValidationQueueItem(BaseModel):
    """An item in the validation queue."""
    id: str
    type: str
    shadow_doc_id: Optional[str] = None
    article_id: str
    article_title: str
    source_name: str
    source_type: SourceType
    created_at: datetime
    urgency: str = "normal"