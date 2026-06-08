#!/usr/bin/env python3
"""
Visualizer Server Entry Point

Executed by Docker. Serves the Wikipedia-like Visualizer.
Run: uvicorn visualizer_server:app --host 0.0.0.0 --port 8000
"""

import os
import sys
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Add 'app' directory (for ontology imports from ilhas_repository)
app_dir = project_root / "app"
if app_dir.exists():
    sys.path.insert(0, str(project_root))

os.chdir(project_root)

from grilo_falante.backend.visualizer.data import VisualizerData

app = FastAPI(title="Grilo Falante Visualizer")

# Setup templates - project root is 2 levels up from visualizer_server/__init__.py
project_root = Path(__file__).parent.parent
BASE_DIR = project_root / "grilo_falante" / "backend" / "visualizer"

from jinja2 import Environment, FileSystemLoader
jinja_env = Environment(loader=FileSystemLoader(str(BASE_DIR / "templates")), auto_reload=False)

def render_template(template_name: str, context: dict):
    """Render a template with the given context."""
    template = jinja_env.get_template(template_name)
    return template.render(**context)

# Static files
STATIC_DIR = BASE_DIR / "static"
if STATIC_DIR.exists():
    app.mount("/visualizer/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Chat static files
CHAT_STATIC_DIR = BASE_DIR / "static" / "chat"
if CHAT_STATIC_DIR.exists():
    app.mount("/chat/static", StaticFiles(directory=str(CHAT_STATIC_DIR)), name="chat_static")

data_fetcher = VisualizerData()


# ============================================================================
# CHAT ROUTES
# ============================================================================

@app.get("/chat")
@app.get("/chat/")
async def chat_index(request: Request):
    """Chat interface - main page."""
    chat_template_path = BASE_DIR / "templates" / "chat" / "index.html"
    if chat_template_path.exists():
        with open(chat_template_path, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    return HTMLResponse("<h1>Chat not found</h1>", status_code=404)


@app.get("/visualizer")
@app.get("/visualizer/")
async def index(request: Request):
    """Main visualizer index."""
    try:
        from grilo_falante.backend.db.connection import init_pool
        await init_pool()
        
        ilhas = await data_fetcher.get_ilhas(limit=20)
        claims = await data_fetcher.get_claims(limit=20)
        sources = await data_fetcher.get_sources(limit=10)
        gaps = await data_fetcher.get_gaps(limit=10)
        
        html = render_template("index.html", {
            "ilhas": ilhas,
            "claims": claims,
            "sources": sources,
            "gaps": gaps,
            "active_tab": "overview",
            "query": "",
        })
        return HTMLResponse(html)
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        return HTMLResponse(f"""
        <html><body style="font-family: sans-serif; padding: 2rem;">
            <h1>Error</h1>
            <p style="color: red;">{e}</p>
            <pre style="background: #f0f0f0; padding: 1rem; overflow: auto;">{tb}</pre>
        </body></html>
        """, status_code=500)


@app.get("/visualizer/ilhas")
async def list_ilhas(request: Request):
    from grilo_falante.backend.db.connection import init_pool
    await init_pool()
    ilhas = await data_fetcher.get_ilhas(limit=50)
    html = render_template("ilhas.html", {"ilhas": ilhas})
    return HTMLResponse(html)


@app.get("/visualizer/claims")
async def list_claims(request: Request):
    from grilo_falante.backend.db.connection import init_pool
    await init_pool()
    claims = await data_fetcher.get_claims(limit=100)
    html = render_template("claims.html", {"claims": claims})
    return HTMLResponse(html)


@app.get("/visualizer/graph")
async def view_graph(request: Request):
    from grilo_falante.backend.db.connection import init_pool
    await init_pool()
    graph = await data_fetcher.get_graph(limit=100)
    graph_dict = graph.to_dict()
    nodes_plain = [
        {"id": n["id"], "label": n["label"], "node_type": n["node_type"], "gmif_level": n.get("gmif_level")}
        for n in graph_dict["nodes"]
    ]
    html = render_template("graph.html", {"nodes": nodes_plain, "edges": graph_dict["edges"]})
    return HTMLResponse(html)


@app.get("/visualizer/sources")
async def list_sources(request: Request):
    from grilo_falante.backend.db.connection import init_pool
    await init_pool()
    sources = await data_fetcher.get_sources(limit=50)
    html = render_template("sources.html", {"sources": sources})
    return HTMLResponse(html)


@app.get("/visualizer/gaps")
async def list_gaps(request: Request):
    from grilo_falante.backend.db.connection import init_pool
    await init_pool()
    gaps = await data_fetcher.get_gaps(limit=50)
    html = render_template("gaps.html", {"gaps": gaps})
    return HTMLResponse(html)


@app.get("/visualizer/search")
async def search(request: Request, q: str):
    from grilo_falante.backend.db.connection import init_pool
    await init_pool()
    results = await data_fetcher.search(q, limit=30)
    html = render_template("search.html", {"query": q, "results": results})
    return HTMLResponse(html)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "visualizer"}


@app.get("/")
async def root():
    """Landing page - Hub with all services."""
    hub_path = project_root / "hub" / "index.html"
    if hub_path.exists():
        return FileResponse(hub_path)
    return HTMLResponse("<h1>Grilo Falante Hub not found</h1>", status_code=404)


@app.get("/hub")
@app.get("/hub/")
async def hub():
    """Hub page - landing page with links to Chat/Visualizer/Graph."""
    hub_path = project_root / "hub" / "index.html"
    if hub_path.exists():
        return FileResponse(hub_path)
    return HTMLResponse("<h1>Hub not found</h1>", status_code=404)