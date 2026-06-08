"""
FastAPI REST API for Grilo Falante v3.0
"""

import hashlib
import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from grilo_falante.config import settings
from grilo_falante.backend.api.auth import AuthMiddleware, verify_api_key
from grilo_falante.backend.db.connection import init_pool, close_pool, check_health, init_schema
from grilo_falante.backend.db.repositories import (
    ClaimRepository,
    GapRepository,
    CuratorRepository,
    SourceRepository,
    SessionPreferencesRepository,
    GovernanceRepository,
    ShadowDocumentRepository,
    StudyPlanRepository,
    generate_key,
    generate_gfid,
)
from grilo_falante.backend.services import (
    GFIDService,
    GMIFClassifier,
    FeynmanService,
    GapDetectionService,
    CuratorScoringService,
    QueryPipeline,
    SchoolModeService,
    CognitiveLint,
)
from grilo_falante.backend.services.llm import get_llm_service
from grilo_falante.models import (
    GovernedClaim,
    Gap,
    Curator,
    GovernedSource,
    SessionPreferences,
    GMIFLevel,
    GapStatus,
    GapType,
    CuratorType,
    ValidationState,
    LegitimacyState,
    GovernanceRecord,
)


app = FastAPI(
    title="Grilo Falante v3.0",
    description="Epistemic Governance Regime API",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.requires_api_token:
    app.add_middleware(AuthMiddleware)


@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup."""
    await init_pool()
    try:
        async with close_pool.__self__.acquire_connection() as conn:
            await init_schema(conn)
    except Exception:
        pass


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown."""
    await close_pool()


# Request/Response models
class CreateClaimRequest(BaseModel):
    claim_key: str
    claim_text: str
    source_id: Optional[int] = None
    session_id: str = "api"
    gmif_level: str = "M4"
    gmif_confidence: float = 0.5


class ValidateClaimRequest(BaseModel):
    curator_id: int
    decision: str
    notes: Optional[str] = None
    evaluator_confidence: Optional[float] = None


class CreateGapRequest(BaseModel):
    query: str
    gap_type: str = "tipo_a_failure"
    reason: str
    session_id: str = "api"


class CreateCuratorRequest(BaseModel):
    curator_key: str
    name: str
    curator_type: str = "human"
    model_name: Optional[str] = None
    specializations: list[str] = []


class SessionPrefsRequest(BaseModel):
    session_id: str
    topics: list[str] = []
    domains: list[str] = []
    recency_weight: float = 0.3
    preferred_categories: list[str] = ["M1", "M2", "M5", "M7"]
    show_metadata: bool = True
    auto_school_mode: bool = True


class FeynmanRequest(BaseModel):
    topic: str
    level: str = "fep1"


# Health endpoints
@app.get("/health")
async def health():
    """Health check."""
    db_health = await check_health()
    return {"status": "ok", "version": "3.0.0", "database": db_health}


# Query endpoints
@app.post("/api/v1/query")
async def query(
    q: str = Query(..., description="Query string"),
    session_id: str = Query("default", description="Session ID"),
    auto_school_mode: bool = Query(True, description="Auto-trigger school mode"),
):
    """Execute query through epistemic pipeline."""
    pipeline = QueryPipeline()
    result = await pipeline.execute(q, session_id, auto_school_mode)
    return {
        "status": result.status,
        "reason": result.reason,
        "claims": [c.to_card() for c in result.claims],
        "gaps": [g.to_dict() for g in result.gaps],
        "m4_count": result.m4_count,
        "lint_passed": result.lint_passed,
    }


# Claim endpoints
@app.get("/api/v1/claims/{claim_id}")
async def get_claim(claim_id: int):
    """Get claim by ID."""
    repo = ClaimRepository()
    claim = await repo.get_by_id(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim.to_card()


@app.post("/api/v1/claims")
async def create_claim(req: CreateClaimRequest):
    """Create a new claim."""
    repo = ClaimRepository()

    existing = await repo.get_by_key(req.claim_key)
    if existing:
        raise HTTPException(status_code=409, detail="Claim already exists")

    content_hash = hashlib.md5(req.claim_text.encode()).hexdigest()[:6]
    gfid = generate_gfid(content_hash, req.gmif_level)

    claim = GovernedClaim(
        claim_key=req.claim_key,
        claim_text=req.claim_text,
        source_id=req.source_id,
        session_id=req.session_id,
        gmif_level=GMIFLevel(req.gmif_level),
        gmif_confidence=req.gmif_confidence,
        gfid=gfid,
    )
    created = await repo.create(claim)
    return {"id": created.id, "claim_key": created.claim_key, "gfid": created.gfid}


@app.post("/api/v1/claims/{claim_id}/validate")
async def validate_claim(claim_id: int, req: ValidateClaimRequest):
    """Validate a claim."""
    repo = ClaimRepository()
    curator_repo = CuratorRepository()
    gov_repo = GovernanceRepository()

    claim = await repo.get_by_id(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    curator = await curator_repo.get_by_id(req.curator_id)
    if not curator:
        raise HTTPException(status_code=404, detail="Curator not found")

    if curator.accountability_score < 0.3:
        raise HTTPException(status_code=403, detail="Curator is suspended")

    prev_status = claim.validation_status
    new_status = (
        ValidationState.APPROVED if req.decision == "approved" else ValidationState.REJECTED
    )
    new_legitimacy = (
        LegitimacyState.ASSERTED if req.decision == "approved" else LegitimacyState.REJECTED
    )

    await repo.update_validation(claim_id, new_status, new_legitimacy)

    # Governance record
    record = GovernanceRecord(
        record_key=generate_key("gov"),
        entity_type="claim",
        entity_id=claim_id,
        entity_key=claim.claim_key,
        action="validate",
        decision=req.decision,
        previous_state=prev_status,
        new_state=new_status.value,
        curator_id=curator.id,
        curator_key=curator.curator_key,
        curator_confidence=req.evaluator_confidence,
        notes=req.notes,
    )
    await gov_repo.create(record)

    # Update curator score
    scoring = CuratorScoringService()
    if req.decision == "corrected":
        await scoring.reward(curator.id, "Valid correction")
    elif req.decision == "rejected":
        await scoring.penalize(curator.id, "Invalid validation")

    return {"claim_id": claim_id, "decision": req.decision, "new_status": new_status.value}


@app.get("/api/v1/claims/cards")
async def get_claim_cards(
    limit: int = Query(20, le=100),
    session_id: Optional[str] = Query(None),
):
    """Get claim cards for UI."""
    repo = ClaimRepository()
    claims = await repo.search("", session_id, limit)
    return {"claims": [c.to_card() for c in claims], "count": len(claims)}


# Gap endpoints
@app.get("/api/v1/gaps")
async def list_gaps(
    status: Optional[str] = Query(None),
    limit: int = Query(20, le=100),
):
    """List gaps."""
    repo = GapRepository()
    if status:
        gaps = await repo.list_by_status(GapStatus(status), limit)
    else:
        gaps = await repo.list_by_status(GapStatus.IDENTIFIED, limit)
    return {"gaps": [g.to_dict() for g in gaps], "count": len(gaps)}


@app.get("/api/v1/gaps/{gap_key}")
async def get_gap(gap_key: str):
    """Get gap by key."""
    repo = GapRepository()
    gap = await repo.get_by_key(gap_key)
    if not gap:
        raise HTTPException(status_code=404, detail="Gap not found")
    return gap.to_dict()


@app.post("/api/v1/gaps")
async def create_gap(req: CreateGapRequest):
    """Create a new gap."""
    repo = GapRepository()
    gap = Gap(
        gap_key=generate_key("gap"),
        gap_type=GapType(req.gap_type),
        query=req.query,
        reason=req.reason,
        session_id=req.session_id,
    )
    created = await repo.create(gap)
    return {"gap_key": created.gap_key, "status": created.status}


@app.post("/api/v1/gaps/{gap_key}/school-mode")
async def school_mode(gap_key: str):
    """Execute school mode for gap."""
    repo = GapRepository()
    gap = await repo.get_by_key(gap_key)
    if not gap:
        raise HTTPException(status_code=404, detail="Gap not found")

    service = SchoolModeService()
    result = await service.execute(gap)

    return {
        "success": result.success,
        "gap_key": result.gap.gap_key,
        "sources_found": result.sources_found,
        "claims_created": result.claims_created,
        "error": result.error,
    }


# PINA endpoints
@app.get("/api/v1/pina/pending")
async def get_pina_pending(limit: int = Query(20, le=100)):
    """Get all pending NCA candidates awaiting human decision."""
    from grilo_falante.regime import Acordar, Loader, Ledger

    ledger = Ledger()
    loader = Loader(ledger=ledger)
    pina = loader.pina
    pending = pina.get_pending()
    return {
        "pending_count": len(pending),
        "pending": pending[:limit],
    }


@app.get("/api/v1/pina/invariants")
async def get_pina_invariants():
    """Get all active invariants (incorporated rules)."""
    from grilo_falante.regime import Acordar, Loader, Ledger

    ledger = Ledger()
    loader = Loader(ledger=ledger)
    pina = loader.pina
    invariants = pina.get_active_invariants()
    return {
        "invariant_count": len(invariants),
        "invariants": invariants,
    }


@app.get("/api/v1/pina/status")
async def get_pina_status():
    """Get full PINA protocol status."""
    from grilo_falante.regime import Acordar, Loader, Ledger

    ledger = Ledger()
    loader = Loader(ledger=ledger)
    pina = loader.pina
    return pina.get_status()


# Curator endpoints
@app.post("/api/v1/curators")
async def create_curator(req: CreateCuratorRequest):
    """Create a new curator."""
    repo = CuratorRepository()
    existing = await repo.get_by_key(req.curator_key)
    if existing:
        raise HTTPException(status_code=409, detail="Curator already exists")

    curator = Curator(
        curator_key=req.curator_key,
        name=req.name,
        curator_type=CuratorType(req.curator_type),
        model_name=req.model_name,
        specializations=req.specializations,
    )
    created = await repo.create(curator)
    return {
        "id": created.id,
        "curator_key": created.curator_key,
        "accountability_score": created.accountability_score,
    }


@app.get("/api/v1/curators/{curator_id}")
async def get_curator(curator_id: int):
    """Get curator by ID."""
    repo = CuratorRepository()
    curator = await repo.get_by_id(curator_id)
    if not curator:
        raise HTTPException(status_code=404, detail="Curator not found")
    return {
        "id": curator.id,
        "curator_key": curator.curator_key,
        "name": curator.name,
        "curator_type": curator.curator_type.value
        if hasattr(curator.curator_type, "value")
        else curator.curator_type,
        "accountability_score": curator.accountability_score,
        "specializations": curator.specializations,
    }


# Source endpoints
@app.get("/api/v1/sources")
async def list_sources(limit: int = Query(20, le=100)):
    """List governed sources."""
    repo = SourceRepository()
    sources = await repo.list_all(limit)
    return {
        "sources": [
            {
                "id": s.id,
                "source_key": s.source_key,
                "title": s.title,
                "authors": s.authors,
                "year": s.year,
            }
            for s in sources
        ],
        "count": len(sources),
    }


# Session endpoints
@app.post("/api/v1/session/preferences")
async def upsert_session_prefs(req: SessionPrefsRequest):
    """Create or update session preferences."""
    repo = SessionPreferencesRepository()
    prefs = SessionPreferences(
        session_id=req.session_id,
        topics=req.topics,
        domains=req.domains,
        recency_weight=req.recency_weight,
        preferred_categories=req.preferred_categories,
        show_metadata=req.show_metadata,
        auto_school_mode=req.auto_school_mode,
    )
    await repo.upsert(prefs)
    return {"status": "ok", "session_id": req.session_id}


@app.get("/api/v1/session/preferences/{session_id}")
async def get_session_prefs(session_id: str):
    """Get session preferences."""
    repo = SessionPreferencesRepository()
    prefs = await repo.get_by_session(session_id)
    if not prefs:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "session_id": prefs.session_id,
        "topics": prefs.topics,
        "domains": prefs.domains,
        "recency_weight": prefs.recency_weight,
        "preferred_categories": prefs.preferred_categories,
    }


# Feynman endpoints
@app.post("/api/v1/feynman/explain")
async def feynman_explain(req: FeynmanRequest):
    """Generate Feynman-style explanation."""
    service = FeynmanService()
    from grilo_falante.backend.services.feynman import FeynmanLevel

    level = FeynmanLevel(req.level)
    result = service.explain(req.topic, level)
    return {
        "level": result.level.value,
        "explanation": result.explanation,
        "concepts": result.concepts_identified,
        "gaps": result.gaps_found,
        "completed": result.completed,
    }


# Document Ingestion endpoints
class PDFIngestRequest(BaseModel):
    source_key: str
    title: str
    authors: list[str] = []
    source_type: str = "paper"


@app.post("/api/v1/ingest/pdf")
async def ingest_pdf(
    file: UploadFile = File(...),
    req: PDFIngestRequest = Depends(),
):
    """
    Upload and process a PDF document.

    The PDF is parsed using OpenDataLoader (local mode),
    then a Shadow Document is automatically generated.
    """
    from grilo_falante.backend.ingestion import PDFIngestionService, ShadowDocumentGenerator
    from grilo_falante.backend.db.repositories import SourceRepository, ShadowDocumentRepository

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        content = await file.read()
        f.write(content)

    pdf_service = PDFIngestionService()
    parse_result = await pdf_service.parse(temp_path)

    if not parse_result.success:
        raise HTTPException(status_code=500, detail=f"PDF parsing failed: {parse_result.error}")

    source_repo = SourceRepository()
    existing = await source_repo.get_by_key(req.source_key)
    if existing:
        raise HTTPException(status_code=409, detail="Source already exists")

    from grilo_falante.models import GovernedSource

    source = GovernedSource(
        source_key=req.source_key,
        title=req.title,
        authors=req.authors,
        source_type=req.source_type,
        source_origin="pdf_upload",
        ingestion_origin="pdf_upload",
        tier="tier_2",
    )
    created_source = await source_repo.create(source)

    markdown_content = ""
    if parse_result.markdown_path:
        markdown_content = await pdf_service.extract_markdown(parse_result.markdown_path)

    if markdown_content:
        shadow_generator = ShadowDocumentGenerator()
        gen_result = await shadow_generator.generate(
            source_title=req.title,
            source_content=markdown_content,
            source_authors=req.authors,
            source_type=req.source_type,
        )

        if gen_result.success:
            shadow_repo = ShadowDocumentRepository()
            shadow_model = gen_result.shadow_document
            shadow_record = ShadowDocument(
                source_id=created_source.id,
                factual_summary=shadow_model.scope,
                projected_claims=shadow_model.assumptions,
                limits=shadow_model.limits,
                misuse_risks=shadow_model.misuse_risks,
                status="completed",
                validation_notes=shadow_model.honesty_note,
                f1_count=shadow_model.f1_count,
                f2_count=shadow_model.f2_count,
            )
            await shadow_repo.create(shadow_record)

    os.unlink(temp_path)

    return {
        "status": "success",
        "source_id": created_source.id,
        "source_key": created_source.source_key,
        "pages_processed": parse_result.pages_processed,
        "shadow_document_generated": gen_result.success if markdown_content else False,
    }


@app.get("/api/v1/shadow/{source_id}")
async def get_shadow_document(source_id: int):
    """Get shadow document for a source."""
    repo = ShadowDocumentRepository()
    shadow = await repo.get_by_source(source_id)
    if not shadow:
        raise HTTPException(status_code=404, detail="Shadow document not found")
    return shadow


# Governance endpoints
@app.get("/api/v1/governance/{entity_type}/{entity_id}")
async def get_governance_history(entity_type: str, entity_id: int):
    """Get governance history for entity."""
    repo = GovernanceRepository()
    records = await repo.get_by_entity(entity_type, entity_id)
    return {"records": [r.to_ledger_entry() for r in records], "count": len(records)}


# Learning Path endpoints
class LearningPathRequest(BaseModel):
    topic: str
    gap_key: Optional[str] = None
    current_knowledge: list[str] = []


@app.post("/api/v1/learning-path")
async def create_learning_path(req: LearningPathRequest):
    """Generate a learning path for a topic."""
    from grilo_falante.cognitive import KanbanEpistemico, MovementType

    kanban = KanbanEpistemico()
    movement = kanban.create_movement(
        title=f"Learning Path: {req.topic}",
        description=f"Auto-generated learning path for: {req.topic}",
        movement_type=MovementType.PROPOSAL,
    )

    return {
        "plan_key": movement.movement_key,
        "topic": req.topic,
        "status": "identified",
        "steps": [
            {"step": 1, "action": f"Research {req.topic}", "status": "pending"},
            {"step": 2, "action": "Identify knowledge gaps", "status": "pending"},
            {"step": 3, "action": "Create shadow document", "status": "pending"},
            {"step": 4, "action": "Extract claims", "status": "pending"},
            {"step": 5, "action": "Validate with curator", "status": "pending"},
        ],
    }


# Trusted Source Registry endpoints
@app.get("/api/v1/registry/sources")
async def get_trusted_sources():
    """Get trusted source registry."""
    repo = SourceRepository()
    sources = await repo.list_all(limit=100)
    return {
        "sources": [
            {
                "id": s.id,
                "source_key": s.source_key,
                "title": s.title,
                "tier": s.tier.value if hasattr(s.tier, "value") else s.tier,
                "validation_status": s.validation_status.value
                if hasattr(s.validation_status, "value")
                else s.validation_status,
            }
            for s in sources
        ],
        "count": len(sources),
    }


class SourceProposalRequest(BaseModel):
    source_key: str
    action: str  # propose_add, propose_remove, propose_tier_change
    rationale: str
    proposer: str = "system"


@app.post("/api/v1/registry/proposals")
async def create_source_proposal(req: SourceProposalRequest):
    """Propose a change to the trusted source registry."""
    return {
        "proposal_key": f"prop_{generate_key('proposal')}",
        "source_key": req.source_key,
        "action": req.action,
        "status": "pending_review",
        "rationale": req.rationale,
    }


# Graph endpoints
@app.get("/api/v1/graph/dot")
async def get_graph_dot():
    """Get epistemic graph in DOT format."""
    repo = ClaimRepository()
    claims = await repo.list_all(limit=100)

    dot_lines = [
        "digraph epistemic_graph {",
        "  rankdir=TB;",
        "  node [shape=box];",
    ]

    for claim in claims:
        gmif = claim.gmif_level.value if hasattr(claim.gmif_level, "value") else claim.gmif_level
        dot_lines.append(
            f'  "{claim.claim_key}" [label="{claim.claim_text[:50]}...", gmif="{gmif}"];'
        )

    dot_lines.append("}")

    return {"dot": "\n".join(dot_lines), "claim_count": len(claims)}


# Claim Card endpoint
@app.get("/api/v1/claims/{claim_id}/card")
async def get_claim_card(claim_id: int):
    """Get claim card for UI display."""
    repo = ClaimRepository()
    claim = await repo.get_by_id(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    gmif = claim.gmif_level.value if hasattr(claim.gmif_level, "value") else claim.gmif_level
    validation = (
        claim.validation_status.value
        if hasattr(claim.validation_status, "value")
        else claim.validation_status
    )

    return {
        "id": claim.id,
        "gfid": claim.gfid,
        "claim_key": claim.claim_key,
        "claim_text": claim.claim_text,
        "gmif_level": gmif,
        "gmif_confidence": claim.gmif_confidence,
        "validation_status": validation,
        "legitimacy_state": claim.legitimacy_state.value
        if hasattr(claim.legitimacy_state, "value")
        else claim.legitimacy_state,
        "attribution": claim.attribution.value
        if hasattr(claim.attribution, "value")
        else claim.attribution,
        "epistemic_role": claim.epistemic_role.value
        if hasattr(claim.epistemic_role, "value")
        else claim.epistemic_role,
        "created_at": claim.created_at.isoformat() if claim.created_at else None,
    }


# Kanban endpoints
@app.get("/api/v1/kanban")
async def get_kanban_state():
    """Get current kanban epistemico state."""
    from grilo_falante.cognitive import KanbanEpistemico

    kanban = KanbanEpistemico()
    state = kanban.get_state()
    return state.to_dict()


class CreateMovementRequest(BaseModel):
    title: str
    description: str = ""
    movement_type: str = "idea"
    author: str = "api"


@app.post("/api/v1/kanban/movements")
async def create_kanban_movement(req: CreateMovementRequest):
    """Create a new epistemic movement."""
    from grilo_falante.cognitive import KanbanEpistemico, MovementType

    kanban = KanbanEpistemico()
    mov_type = (
        MovementType(req.movement_type)
        if req.movement_type in [m.value for m in MovementType]
        else MovementType.IDEA
    )

    movement = kanban.create_movement(
        title=req.title,
        description=req.description,
        movement_type=mov_type,
        author=req.author,
    )

    return {
        "movement_key": movement.movement_key,
        "title": movement.title,
        "column": movement.column.value,
        "status": "created",
    }


# Audit endpoints
class RunAuditRequest(BaseModel):
    session_id: Optional[str] = None
    limit: int = 50


@app.post("/api/v1/audit")
async def run_hostile_audit(req: RunAuditRequest):
    """Run hostile audit on claims."""
    from grilo_falante.cognitive import AuditoriaHostil

    claim_repo = ClaimRepository()
    gov_repo = GovernanceRepository()

    claims = await claim_repo.search("", limit=req.limit)
    gov_records = await gov_repo.list_recent(limit=100)

    audit = AuditoriaHostil()
    report = await audit.run_full_audit(
        claims=[c.to_dict() for c in claims],
        governance_records=[r.to_ledger_entry() for r in gov_records],
    )

    return report.to_dict()


# Prompt workflow endpoints
class TriagemRequest(BaseModel):
    conversation_content: str


@app.post("/api/v1/prompts/triagem")
async def run_triagem(req: TriagemRequest):
    """Execute TRIAGEM_E_PRESERVACAO workflow."""
    from grilo_falante.cognitive import PromptWorkflows

    workflows = PromptWorkflows()
    result = workflows.triagem_workflow(req.conversation_content)
    return result


class RadiografiaRequest(BaseModel):
    conversation_content: str


@app.post("/api/v1/prompts/radiografia")
async def run_radiografia(req: RadiografiaRequest):
    """Execute RADIOGRAFIA_ERROS workflow."""
    from grilo_falante.cognitive import PromptWorkflows

    workflows = PromptWorkflows()
    result = workflows.radiografia_workflow(req.conversation_content)
    return result


# ============================================================================
# CHAT API - Integrated chat with epistemic governance
# ============================================================================

import json
from fastapi import BackgroundTasks
from fastapi.responses import StreamingResponse

chat_service = None

def get_chat_service():
    global chat_service
    if chat_service is None:
        from grilo_falante.backend.services.chat_service import ChatService
        chat_service = ChatService()
    return chat_service


class ChatConversationRequest(BaseModel):
    title: str = "New Conversation"
    model: Optional[str] = None


class ChatMessageRequest(BaseModel):
    conversation_key: str
    message: str


@app.get("/api/v1/chat/conversations")
async def list_conversations(user_id: str = Query("anonymous", description="User ID")):
    """List all conversations for a user."""
    service = get_chat_service()
    conversations = await service.list_conversations(user_id=user_id, limit=50)
    return {
        "conversations": [c.to_summary() for c in conversations],
        "count": len(conversations),
    }


@app.post("/api/v1/chat/conversations")
async def create_conversation(
    req: ChatConversationRequest = None,
    user_id: str = Query("anonymous", description="User ID"),
):
    """Create a new conversation."""
    service = get_chat_service()
    conversation = await service.create_conversation(
        user_id=user_id,
        title=req.title if req else "New Conversation",
        model=req.model if req else None,
    )
    return conversation.to_summary()


@app.get("/api/v1/chat/conversations/{conversation_key}")
async def get_conversation(conversation_key: str):
    """Get a conversation with its messages."""
    service = get_chat_service()
    conversation = await service.get_conversation(conversation_key)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = await service.get_messages(conversation_key)

    return {
        "conversation": conversation.to_summary(),
        "messages": [m.to_dict() for m in messages],
    }


@app.delete("/api/v1/chat/conversations/{conversation_key}")
async def delete_conversation(conversation_key: str):
    """Delete a conversation (GDPR compliance)."""
    service = get_chat_service()
    conversation = await service.get_conversation(conversation_key)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    repo = service.conversation_repo
    await repo.delete(conversation_key)
    return {"status": "deleted", "conversation_key": conversation_key}


@app.post("/api/v1/chat/message")
async def send_message(
    req: ChatMessageRequest,
    user_id: str = Query("anonymous", description="User ID"),
):
    """Send a message and get streaming response."""
    service = get_chat_service()

    async def event_generator():
        async for event in service.process_message_streaming(
            conversation_key=req.conversation_key,
            message=req.message,
            user_id=user_id,
        ):
            event_type = event.get("type", "message")
            event_data = event.get("data", {})

            if event_type == "chunk":
                yield f"event: chunk\ndata: {json.dumps(event_data)}\n\n".encode()
            elif event_type == "claim":
                yield f"event: claim\ndata: {json.dumps(event_data)}\n\n".encode()
            elif event_type == "gap":
                yield f"event: gap\ndata: {json.dumps(event_data)}\n\n".encode()
            elif event_type == "done":
                yield f"event: done\ndata: {json.dumps(event_data)}\n\n".encode()
            else:
                yield f"event: info\ndata: {json.dumps(event_data)}\n\n".encode()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/v1/chat/conversations/{conversation_key}/claims")
async def get_conversation_claims(conversation_key: str):
    """Get all claims detected in a conversation."""
    service = get_chat_service()
    messages = await service.get_messages(conversation_key)

    claim_ids = set()
    for msg in messages:
        claim_ids.update(msg.claims_detected)

    claims = []
    for claim_id in claim_ids:
        claim = await service.claim_repo.get_by_id(claim_id)
        if claim:
            claims.append(claim.to_card())

    return {"claims": claims, "count": len(claims)}


@app.get("/api/v1/chat/conversations/{conversation_key}/gaps")
async def get_conversation_gaps(conversation_key: str):
    """Get all gaps identified in a conversation."""
    service = get_chat_service()
    messages = await service.get_messages(conversation_key)

    gap_ids = set()
    for msg in messages:
        gap_ids.update(msg.gaps_identified)

    gaps = []
    for gap_id in gap_ids:
        gap = await service.gap_repo.get_by_id(gap_id)
        if gap:
            gaps.append(gap.to_dict())

    return {"gaps": gaps, "count": len(gaps)}


# ============================================================================
# MANUAL API - RAG-ready documentation server
# ============================================================================

import os
from pathlib import Path

MANUAL_PATH = Path(__file__).parent.parent.parent.parent / "docs" / "manual"


@app.get("/api/v1/manual/")
async def get_manual_index():
    """
    Get index of all manual chapters for navigation.

    Returns:
        List of chapters with titles and paths
    """
    if not MANUAL_PATH.exists():
        return {"error": "Manual not found", "chapters": []}

    chapters = []
    for part_dir in sorted(MANUAL_PATH.iterdir()):
        if part_dir.is_dir() and part_dir.name.startswith("PARTE"):
            for md_file in sorted(part_dir.glob("*.md")):
                chapters.append(
                    {
                        "path": str(md_file.relative_to(MANUAL_PATH)),
                        "file": md_file.name,
                        "title": _extract_title(md_file),
                        "part": part_dir.name,
                    }
                )
        elif part_dir.name == "APENDICES":
            for md_file in sorted(part_dir.glob("*.md")):
                chapters.append(
                    {
                        "path": str(md_file.relative_to(MANUAL_PATH)),
                        "file": md_file.name,
                        "title": _extract_title(md_file),
                        "part": "APENDICES",
                    }
                )
        elif part_dir.name == "00_INDICE.md":
            chapters.insert(
                0,
                {
                    "path": "00_INDICE.md",
                    "file": "00_INDICE.md",
                    "title": "Índice Geral",
                    "part": "ROOT",
                },
            )

    return {
        "chapters": chapters,
        "count": len(chapters),
    }


@app.get("/api/v1/manual/{chapter_path:path}")
async def get_manual_chapter(chapter_path: str):
    """
    Get specific manual chapter content.

    Supports RAG by returning structured content.
    """
    if ".." in chapter_path:
        raise HTTPException(status_code=400, detail="Invalid path")

    file_path = MANUAL_PATH / chapter_path

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Chapter not found: {chapter_path}")

    if not file_path.is_file():
        raise HTTPException(status_code=400, detail="Not a file")

    content = file_path.read_text(encoding="utf-8")

    sections = _extract_sections(content)

    return {
        "path": chapter_path,
        "title": _extract_title(file_path),
        "content": content,
        "sections": sections,
        "word_count": len(content.split()),
    }


@app.get("/api/v1/manual/search")
async def search_manual(q: str = Query(..., min_length=2)):
    """
    Search within manual content.

    For RAG integration - returns relevant sections.
    """
    if not MANUAL_PATH.exists():
        return {"error": "Manual not found", "results": []}

    results = []
    search_lower = q.lower()

    for md_file in MANUAL_PATH.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
            lines = content.split("\n")

            for i, line in enumerate(lines, 1):
                if search_lower in line.lower():
                    context_before = "\n".join(lines[max(0, i - 3) : i])
                    context_after = "\n".join(lines[i : min(len(lines), i + 2)])

                    results.append(
                        {
                            "file": str(md_file.relative_to(MANUAL_PATH)),
                            "line": i,
                            "match": line.strip(),
                            "context_before": context_before,
                            "context_after": context_after,
                        }
                    )

                    if len(results) >= 20:
                        break
        except Exception:
            continue

    results.sort(key=lambda x: x["line"])

    return {
        "query": q,
        "results": results,
        "count": len(results),
    }


def _extract_title(file_path: Path) -> str:
    """Extract title from markdown file."""
    try:
        content = file_path.read_text(encoding="utf-8")
        for line in content.split("\n")[:10]:
            line = line.strip()
            if line.startswith("# "):
                return line[2:].strip()
        return file_path.stem
    except Exception:
        return file_path.stem


def _extract_sections(content: str) -> list[dict]:
    """Extract sections from markdown for RAG."""
    sections = []
    current_section = {"level": 0, "title": "", "content": []}

    for line in content.split("\n"):
        if line.startswith("#"):
            if current_section["content"] or current_section["title"]:
                sections.append(current_section)

            level = len(line) - len(line.lstrip("#"))
            current_section = {
                "level": level,
                "title": line.strip("# ").strip(),
                "content": [],
            }
        else:
            current_section["content"].append(line)

    if current_section["content"] or current_section["title"]:
        sections.append(current_section)

    return sections
