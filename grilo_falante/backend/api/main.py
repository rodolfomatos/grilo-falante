"""
FastAPI REST API for Grilo Falante v3.0
"""

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from grilo_falante.backend.db.connection import init_pool, close_pool, check_health, init_schema
from grilo_falante.backend.db.repositories import (
    ClaimRepository,
    GapRepository,
    CuratorRepository,
    SourceRepository,
    SessionPreferencesRepository,
    GovernanceRepository,
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
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    await init_pool()
    try:
        async with close_pool.__self__.acquire_connection() as conn:
            await init_schema(conn)
    except Exception:
        pass  # Schema might already exist
    yield
    await close_pool()


app = FastAPI(
    title="Grilo Falante v3.0",
    description="Epistemic Governance Regime API",
    version="3.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    new_status = ValidationState.APPROVED if req.decision == "approved" else ValidationState.REJECTED
    new_legitimacy = LegitimacyState.ASSERTED if req.decision == "approved" else LegitimacyState.REJECTED

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
        "curator_type": curator.curator_type.value if hasattr(curator.curator_type, 'value') else curator.curator_type,
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


# Governance endpoints
@app.get("/api/v1/governance/{entity_type}/{entity_id}")
async def get_governance_history(entity_type: str, entity_id: int):
    """Get governance history for entity."""
    repo = GovernanceRepository()
    records = await repo.get_by_entity(entity_type, entity_id)
    return {"records": [r.to_ledger_entry() for r in records], "count": len(records)}


import hashlib
