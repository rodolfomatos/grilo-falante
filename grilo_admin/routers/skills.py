"""
Skills Router - Shadow First API

Provides endpoints for:
- Shadow debt check
- Shadow session management
- Concept registry
- Ritual and status
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from grilo_admin.auth import get_current_user, require_role
from grilo_admin.models import User, UserRole
from grilo_admin.skills import ShadowFirstSkill, ConceptRegistry

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/skills", tags=["skills"])


class ShadowContentRequest(BaseModel):
    """Request to add shadow content."""
    content: str
    sources: Optional[List[str]] = None


class FAQRequest(BaseModel):
    """Request to add FAQ entry."""
    question: str
    answer: Optional[str] = None


class ReportRequest(BaseModel):
    """Request to generate report."""
    theme: str
    concepts: List[str]


class RegisterConceptRequest(BaseModel):
    """Request to register a concept."""
    name: str
    mentioned_by: Optional[str] = None
    priority: str = "medium"
    notes: str = ""


class UpdateConceptRequest(BaseModel):
    """Request to update concept status."""
    status: Optional[str] = None
    shadow_doc_path: Optional[str] = None
    faq_path: Optional[str] = None
    report_path: Optional[str] = None
    related_concepts: Optional[List[str]] = None
    notes: Optional[str] = None


# Response models
class ConceptStatusResponse(BaseModel):
    """Response for concept check."""
    status: str
    concept: str
    registered: bool
    shadow_score: int = 0
    recommendation: str
    shadow_doc: bool = False
    faq: bool = False
    report: bool = False


class ShadowSessionResponse(BaseModel):
    """Response for shadow session."""
    concept: str
    started_at: str
    completed_at: Optional[str] = None
    has_content: bool
    faqs_count: int
    gaps_count: int
    sources_count: int


class RitualResponse(BaseModel):
    """Response for ritual."""
    total_concepts: int
    shadow_debt_count: int
    avg_shadow_score: float
    shadow_debt: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]


class StatusResponse(BaseModel):
    """Response for status."""
    total_concepts: int
    complete: int
    partial: int
    undocumented: int
    avg_shadow_score: float
    completeness_pct: float
    complete_concepts: List[str]
    partial_concepts: List[str]
    shadow_debt_concepts: List[str]


class ReportResponse(BaseModel):
    """Response for report."""
    theme: str
    generated_at: str
    concepts_documented: int
    shadow_debt_resolved: int
    gaps_identified: List[str]
    next_steps: List[str]


def get_skill() -> ShadowFirstSkill:
    """Get ShadowFirstSkill instance."""
    return ShadowFirstSkill()


def get_registry() -> ConceptRegistry:
    """Get ConceptRegistry instance."""
    return ConceptRegistry()


# Shadow First Endpoints
@router.get("/shadow/check/{concept}", response_model=ConceptStatusResponse)
async def check_concept(
    concept: str,
    current_user: User = Depends(get_current_user),
):
    """
    Check if a concept is documented.

    Returns the concept's shadow status, score, and recommendations.
    """
    skill = get_skill()
    result = skill.check(concept)

    return ConceptStatusResponse(
        status=result.get("status", "unknown"),
        concept=result.get("concept", concept),
        registered=result.get("registered", False),
        shadow_score=result.get("shadow_score", 0),
        recommendation=result.get("recommendation", ""),
        shadow_doc=result.get("shadow_doc", False),
        faq=result.get("faq", False),
        report=result.get("report", False),
    )


@router.post("/shadow/session/{concept}")
async def start_session(
    concept: str,
    current_user: User = Depends(get_current_user),
):
    """
    Start a shadow documentation session for a concept.
    """
    skill = get_skill()
    session = skill.shadow(concept)

    return ShadowSessionResponse(
        concept=session.concept,
        started_at=session.started_at,
        completed_at=session.completed_at,
        has_content=session.shadow_doc is not None,
        faqs_count=len(session.faqs),
        gaps_count=len(session.gaps),
        sources_count=len(session.sources_used),
    )


@router.get("/shadow/session/{concept}", response_model=ShadowSessionResponse)
async def get_session(
    concept: str,
    current_user: User = Depends(get_current_user),
):
    """
    Get a shadow session for a concept.
    """
    skill = get_skill()
    session = skill.get_session(concept)

    if not session:
        raise HTTPException(status_code=404, detail=f"Session for '{concept}' not found")

    return ShadowSessionResponse(
        concept=session.concept,
        started_at=session.started_at,
        completed_at=session.completed_at,
        has_content=session.shadow_doc is not None,
        faqs_count=len(session.faqs),
        gaps_count=len(session.gaps),
        sources_count=len(session.sources_used),
    )


@router.post("/shadow/session/{concept}/content")
async def add_content(
    concept: str,
    request: ShadowContentRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Add shadow document content for a concept.
    """
    skill = get_skill()
    skill.add_shadow_content(concept, request.content, sources=request.sources)

    return {"success": True, "message": f"Content added for '{concept}'"}


@router.post("/shadow/session/{concept}/faq")
async def add_faq(
    concept: str,
    request: FAQRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Add an FAQ entry for a concept.
    """
    skill = get_skill()
    skill.add_faq(concept, request.question, answer=request.answer)

    return {"success": True, "message": f"FAQ added for '{concept}'"}


@router.post("/shadow/session/{concept}/complete")
async def complete_session(
    concept: str,
    current_user: User = Depends(get_current_user),
):
    """
    Mark a shadow session as complete.
    """
    skill = get_skill()
    success = skill.complete_session(concept)

    if not success:
        raise HTTPException(status_code=404, detail=f"Session for '{concept}' not found")

    return {"success": True, "message": f"Session for '{concept}' completed"}


@router.get("/shadow/ritual", response_model=RitualResponse)
async def ritual(
    current_user: User = Depends(get_current_user),
):
    """
    Run the pre-session ritual - check shadow debt.

    Returns all concepts that need documentation.
    """
    skill = get_skill()
    result = skill.ritual()

    return RitualResponse(
        total_concepts=result["total_concepts"],
        shadow_debt_count=result["shadow_debt_count"],
        avg_shadow_score=result["avg_shadow_score"],
        shadow_debt=result["shadow_debt"],
        recommendations=result["recommendations"],
    )


@router.get("/shadow/status", response_model=StatusResponse)
async def status(
    current_user: User = Depends(get_current_user),
):
    """
    Get overall shadow documentation status.
    """
    skill = get_skill()
    result = skill.status()

    return StatusResponse(
        total_concepts=result["total_concepts"],
        complete=result["complete"],
        partial=result["partial"],
        undocumented=result["undocumented"],
        avg_shadow_score=result["avg_shadow_score"],
        completeness_pct=result["completeness_pct"],
        complete_concepts=result["complete_concepts"],
        partial_concepts=result["partial_concepts"],
        shadow_debt_concepts=result["shadow_debt_concepts"],
    )


@router.post("/shadow/report", response_model=ReportResponse)
async def generate_report(
    request: ReportRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Generate a session report.
    """
    skill = get_skill()
    result = skill.generate_report(request.theme, request.concepts)

    return ReportResponse(
        theme=result["theme"],
        generated_at=result["generated_at"],
        concepts_documented=result["concepts_documented"],
        shadow_debt_resolved=result["shadow_debt_resolved"],
        gaps_identified=result["gaps_identified"],
        next_steps=result["next_steps"],
    )


# Concept Registry Endpoints
@router.get("/registry/concepts")
async def list_concepts(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """
    List all concepts in the registry.
    """
    registry = get_registry()

    if status:
        from grilo_admin.skills.registry import ConceptStatus
        return [c.to_dict() for c in registry.list_by_status(ConceptStatus(status))]
    return [c.to_dict() for c in registry.list_all()]


@router.get("/registry/concepts/{concept}")
async def get_concept(
    concept: str,
    current_user: User = Depends(get_current_user),
):
    """
    Get a concept from the registry.
    """
    registry = get_registry()
    c = registry.get_concept(concept)

    if not c:
        raise HTTPException(status_code=404, detail=f"Concept '{concept}' not found")

    return c.to_dict()


@router.post("/registry/concepts")
async def register_concept(
    request: RegisterConceptRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Register a new concept.
    """
    registry = get_registry()
    concept = registry.register_concept(
        name=request.name,
        mentioned_by=request.mentioned_by,
        priority=request.priority,
        notes=request.notes,
    )

    return {"success": True, "concept": concept.to_dict()}


@router.put("/registry/concepts/{concept}")
async def update_concept(
    concept: str,
    request: UpdateConceptRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Update a concept's documentation status.
    """
    registry = get_registry()

    from grilo_admin.skills.registry import ConceptStatus
    status = ConceptStatus(request.status) if request.status else None

    updated = registry.update_concept(
        name_or_id=concept,
        status=status,
        shadow_doc_path=request.shadow_doc_path,
        faq_path=request.faq_path,
        report_path=request.report_path,
        related_concepts=request.related_concepts,
        notes=request.notes,
    )

    if not updated:
        raise HTTPException(status_code=404, detail=f"Concept '{concept}' not found")

    return {"success": True, "concept": updated.to_dict()}


@router.get("/registry/score")
async def get_score(
    current_user: User = Depends(get_current_user),
):
    """
    Get overall shadow documentation score.
    """
    registry = get_registry()
    return registry.get_shadow_score()


@router.get("/registry/debt")
async def get_debt(
    current_user: User = Depends(get_current_user),
):
    """
    Get all concepts in shadow debt.
    """
    registry = get_registry()
    debt = registry.get_shadow_debt()
    return [c.to_dict() for c in debt]
