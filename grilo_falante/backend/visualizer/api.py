"""
Visualizer API - FastAPI endpoints for Wikipedia-like explorer
"""

from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse
from typing import Optional
from grilo_falante.backend.visualizer.data import VisualizerData


router = APIRouter(prefix="/visualizer", tags=["visualizer"])
data_fetcher = VisualizerData()


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main visualizer index with tabs."""
    from grilo_falante.backend.db.connection import init_pool
    
    await init_pool()
    
    ilhas = await data_fetcher.get_ilhas(limit=20)
    claims = await data_fetcher.get_claims(limit=20)
    sources = await data_fetcher.get_sources(limit=10)
    gaps = await data_fetcher.get_gaps(limit=10)
    
    return request.app.state.renderer.render(
        "visualizer/index.html",
        ilhas=ilhas,
        claims=claims,
        sources=sources,
        gaps=gaps,
        active_tab="overview",
    )


@router.get("/ilhas", response_class=HTMLResponse)
async def list_ilhas(request: Request, limit: int = Query(50, le=100)):
    """List all islands."""
    from grilo_falante.backend.db.connection import init_pool
    
    await init_pool()
    ilhas = await data_fetcher.get_ilhas(limit=limit)
    
    return request.app.state.renderer.render(
        "visualizer/ilhas.html",
        ilhas=ilhas,
    )


@router.get("/ilhas/{key}", response_class=HTMLResponse)
async def view_ilha(request: Request, key: str):
    """View single island article."""
    from grilo_falante.backend.db.connection import init_pool
    
    await init_pool()
    ilha = await data_fetcher.get_ilha_by_key(key)
    
    if not ilha:
        return HTMLResponse("<h1>Ilha not found</h1>", status_code=404)
    
    return request.app.state.renderer.render(
        "visualizer/ilha.html",
        ilha=ilha,
    )


@router.get("/claims", response_class=HTMLResponse)
async def list_claims(request: Request, limit: int = Query(100, le=200)):
    """List all claims."""
    from grilo_falante.backend.db.connection import init_pool
    
    await init_pool()
    claims = await data_fetcher.get_claims(limit=limit)
    
    return request.app.state.renderer.render(
        "visualizer/claims.html",
        claims=claims,
    )


@router.get("/claims/{key}", response_class=HTMLResponse)
async def view_claim(request: Request, key: str):
    """View single claim."""
    from grilo_falante.backend.db.connection import init_pool
    
    await init_pool()
    claims = await data_fetcher.get_claims(limit=500)
    
    claim = None
    for c in claims:
        if c.claim_key == key:
            claim = c
            break
    
    if not claim:
        return HTMLResponse("<h1>Claim not found</h1>", status_code=404)
    
    return request.app.state.renderer.render(
        "visualizer/claim.html",
        claim=claim,
    )


@router.get("/graph", response_class=HTMLResponse)
async def view_graph(request: Request, limit: int = Query(100, le=200)):
    """Knowledge graph visualization."""
    from grilo_falante.backend.db.connection import init_pool
    
    await init_pool()
    graph = await data_fetcher.get_graph(limit=limit)
    
    return request.app.state.renderer.render(
        "visualizer/graph.html",
        nodes=graph.nodes,
        edges=graph.edges,
    )


@router.get("/sources", response_class=HTMLResponse)
async def list_sources(request: Request, limit: int = Query(50, le=100)):
    """List all sources."""
    from grilo_falante.backend.db.connection import init_pool
    
    await init_pool()
    sources = await data_fetcher.get_sources(limit=limit)
    
    return request.app.state.renderer.render(
        "visualizer/sources.html",
        sources=sources,
    )


@router.get("/gaps", response_class=HTMLResponse)
async def list_gaps(request: Request, limit: int = Query(50, le=100)):
    """List all gaps."""
    from grilo_falante.backend.db.connection import init_pool
    
    await init_pool()
    gaps = await data_fetcher.get_gaps(limit=limit)
    
    return request.app.state.renderer.render(
        "visualizer/gaps.html",
        gaps=gaps,
    )


@router.get("/search", response_class=HTMLResponse)
async def search(request: Request, q: str = Query(...)):
    """Search with Google-like results."""
    from grilo_falante.backend.db.connection import init_pool
    
    await init_pool()
    results = await data_fetcher.search(q, limit=30)
    
    return request.app.state.renderer.render(
        "visualizer/search.html",
        query=q,
        results=results,
    )


# JSON API endpoints
@router.get("/api/ilhas")
async def api_ilhas(limit: int = Query(50, le=100)):
    """JSON API for islands."""
    from grilo_falante.backend.db.connection import init_pool
    await init_pool()
    return await data_fetcher.get_ilhas(limit=limit)


@router.get("/api/claims")
async def api_claims(limit: int = Query(100, le=200)):
    """JSON API for claims."""
    from grilo_falante.backend.db.connection import init_pool
    await init_pool()
    return await data_fetcher.get_claims(limit=limit)


@router.get("/api/graph")
async def api_graph(limit: int = Query(100, le=200)):
    """JSON API for graph (D3.js compatible)."""
    from grilo_falante.backend.db.connection import init_pool
    await init_pool()
    graph = await data_fetcher.get_graph(limit=limit)
    
    # Convert to D3.js format
    return {
        "nodes": [{"id": n.id, "label": n.label, "type": n.node_type, "gmif": n.gmif_level} for n in graph.nodes],
        "links": [{"source": e.source, "target": e.target, "type": e.edge_type} for e in graph.edges],
    }


@router.get("/api/search")
async def api_search(q: str = Query(...), limit: int = Query(20, le=50)):
    """JSON API for search."""
    from grilo_falante.backend.db.connection import init_pool
    await init_pool()
    return await data_fetcher.search(q, limit=limit)