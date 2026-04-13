#!/usr/bin/env python3
"""
Grilo Falante API
==============

FastAPI backend para ChatGPT Actions.
Também funciona standalone com Python.

Usage:
    python3 api.py                   # Local dev em http://localhost:8000
    python3 api.py --port 8080       # Porta específica
    # Deploy para Vercel/Cloudflare: ver.vercel.app

Endpoints:
    POST /analyze - Analisa um path
    POST /search - Pesquisa em memórias
    GET  /status - Estado do sistema
"""

import json
import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Grilo Falante API",
    description="Análise epistemológica com GMIF",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ MODELS ============

class AnalyzeRequest(BaseModel):
    path: str
    store: bool = True

class SearchRequest(BaseModel):
    query: str
    limit: int = 5

class IrAEscolaRequest(BaseModel):
    message: str
    max_gaps: int = 5

class ScientificCompilerRequest(BaseModel):
    article_path: str
    analyze_gaps: bool = True

class AnalyzeResponse(BaseModel):
    total_nodes: int
    total_edges: int
    gmif_distribution: dict
    gf_ids: list
    status: str

class SearchResponse(BaseModel):
    results: list
    count: int

class IrAEscolaResponse(BaseModel):
    status: str
    original_message: str
    gaps_detected: list
    sources_used: list
    feynman_child: str
    feynman_expert: str
    why_questions: list
    gf_id: str

class ScientificCompilerResponse(BaseModel):
    status: str
    article_title: str
    claims: list
    evidence: list
    gmif_graph: str
    lint_report: list
    critical_path: list
    fragility_analysis: dict

# ============ CORE FUNCTIONS ============

def run_extract(path: str) -> dict:
    """Extrai conceitos usando graphify."""
    try:
        import sys
        sys.path.insert(0, '/home/rodolfo/.local/lib/python3.10/site-packages')
        from graphify.extract import extract
        from graphify.build import build_from_json
        
        path_obj = Path(path)
        files = list(path_obj.glob("**/*")) if path_obj.is_dir() else [path_obj]
        files = [f for f in files if f.is_file()]
        
        if not files:
            return {"error": "No files found"}
        
        result = extract(files)
        G = build_from_json(result)
        
        nodes = []
        for node_id, data in G.nodes(data=True):
            nodes.append({
                "id": node_id,
                "label": data.get("label", ""),
                "file_type": data.get("file_type", ""),
            })
        
        edges = []
        for src, tgt, data in G.edges(data=True):
            edges.append({
                "source": src,
                "target": tgt,
                "relation": data.get("relation", "related"),
                "confidence": data.get("confidence", "EXTRACTED"),
            })
        
        return {"nodes": nodes, "edges": edges}
        
    except ImportError as e:
        return {"error": f"graphify not available: {e}"}
    except Exception as e:
        return {"error": str(e)}

def classify_gmif(nodes: list, edges: list) -> list:
    """Classifica nodes com GMIF."""
    # Count edge types per node
    edge_counts = {}
    for edge in edges:
        src = edge.get("source", "")
        conf = edge.get("confidence", "EXTRACTED")
        if src not in edge_counts:
            edge_counts[src] = {"EXTRACTED": 0, "INFERRED": 0, "AMBIGUOUS": 0}
        edge_counts[src][conf] = edge_counts[src].get(conf, 0) + 1
    
    for node in nodes:
        node_id = node.get("id", "")
        counts = edge_counts.get(node_id, {})
        
        if counts.get("AMBIGUOUS", 0) > 0:
            gmif = "M4"
        elif counts.get("EXTRACTED", 0) > 0:
            gmif = "M1"
        elif counts.get("INFERRED", 0) > 0:
            gmif = "M5"
        else:
            gmif = "M3"
        
        node["gmif_type"] = gmif
        node["gf_id"] = f"GF-{datetime.now().strftime('%y%m%d')}-{gmif}-{node_id[:6]}"
    
    return nodes

def store_mempalace(nodes: list, edges: list) -> dict:
    """Guarda em MemPalace."""
    try:
        from mempalace.knowledge_graph import KnowledgeGraph
        
        kg = KnowledgeGraph()
        
        for node in nodes:
            gf_id = node.get("gf_id", "")
            gmif = node.get("gmif_type", "M3")
            label = node.get("label", "")[:200]
            
            if gf_id:
                kg.add_triple(gf_id, "has_type", gmif)
                kg.add_triple(gf_id, "claim", label)
        
        for edge in edges:
            src = edge.get("source", "")
            tgt = edge.get("target", "")
            rel = edge.get("relation", "")
            
            if src and tgt:
                kg.add_triple(src, rel, tgt)
        
        return {"status": "ok", "stored": len(nodes)}
        
    except Exception as e:
        # Fallback to JSON file
        output_file = Path("grilo_output.json")
        output = {
            "nodes": nodes,
            "edges": edges,
            "metadata": {"timestamp": datetime.now().isoformat()},
        }
        output_file.write_text(json.dumps(output, indent=2))
        return {"status": "fallback", "stored": len(nodes), "file": str(output_file)}

def search_memories(query: str, limit: int = 5) -> list:
    """Pesquisa em memórias."""
    try:
        from mempalace.searcher import search_memories as mp_search
        
        results = mp_search(query, n_results=limit)
        return results
        
    except Exception as e:
        # Try fallback file
        output_file = Path("grilo_output.json")
        if output_file.exists():
            data = json.loads(output_file.read_text())
            nodes = data.get("nodes", [])
            # Simple text search
            query_lower = query.lower()
            results = [
                n for n in nodes 
                if query_lower in n.get("label", "").lower()
            ][:limit]
            return results
        return []

# ============ ENDPOINTS ============

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    """Analisa um diretório com GMIF."""
    logger.info(f"Analyzing: {req.path}")
    
    # Extract
    extraction = run_extract(req.path)
    if "error" in extraction:
        raise HTTPException(status_code=400, detail=extraction["error"])
    
    nodes = extraction["nodes"]
    edges = extraction["edges"]
    
    # Classify
    classified = classify_gmif(nodes, edges)
    
    # Count GMIF
    gmif_dist = {}
    for n in classified:
        t = n.get("gmif_type", "M3")
        gmif_dist[t] = gmif_dist.get(t, 0) + 1
    
    # Store
    if req.store:
        store_mempalace(classified, edges)
    
    return AnalyzeResponse(
        total_nodes=len(classified),
        total_edges=len(edges),
        gmif_distribution=gmif_dist,
        gf_ids=[n.get("gf_id", "") for n in classified[:10]],
        status="ok"
    )

@app.post("/search", response_model=SearchResponse)  
async def search(req: SearchRequest):
    """Pesquisa em memórias."""
    results = search_memories(req.query, req.limit)
    return SearchResponse(
        results=results,
        count=len(results)
    )

@app.get("/status")
async def status():
    """Estado do sistema."""
    return {
        "status": "ok",
        "version": "2.0.0",
        "services": {
            "graphify": "available",
            "mempalace": "available",
            "ir_a_escola": "available",
            "scientific_compiler": "available",
        }
    }


# ============ NEW ENDPOINTS ============

@app.post("/ir-a-escola", response_model=IrAEscolaResponse)
async def ir_a_escola(req: IrAEscolaRequest):
    """Executa o loop Ir à Escola."""
    logger.info(f"Ir à Escola: {req.message[:50]}...")
    try:
        # Add project root to path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        from app.services.ir_a_escola import IrAEscolaOrchestrator
        from app.services.gap_detector import GapDetector
        from app.services.active_search import ActiveSearcher
        from app.services.feynman_synthesize import FeynmanSynthesizer
        from app.services.why_loop import WhyLoop
        
        # Run gap detection
        detector = GapDetector()
        gaps = detector.detect(req.message, max_gaps=req.max_gaps)
        gap_texts = [g.text for g in gaps]
        
        if not gap_texts:
            return IrAEscolaResponse(
                status="no_gaps",
                original_message=req.message,
                gaps_detected=[],
                sources_used=[],
                feynman_child="Não há factos desconhecidos nesta mensagem.",
                feynman_expert="No gaps detected.",
                why_questions=[],
                gf_id=f"GF-{datetime.now().strftime('%y%m%d')}-NOGAP"
            )
        
        # Run search
        searcher = ActiveSearcher()
        all_results = {}
        for gap in gap_texts:
            results = searcher.search(gap)
            all_results[gap] = [{"content": r.content, "source": r.source} for r in results]
        
        # Run synthesize
        synthesizer = FeynmanSynthesizer()
        combined = []
        for gap in gap_texts:
            combined.extend(all_results.get(gap, []))
        synthesis = synthesizer.synthesize(gap_texts[0], combined)
        
        # Run why loop
        why_loop = WhyLoop()
        why_result = why_loop.run_loop(synthesis, gap_texts[0])
        
        # Generate GF-ID
        gf_id = f"GF-{datetime.now().strftime('%y%m%d')}-ESCOLA-{gap_texts[0][:6]}"
        
        return IrAEscolaResponse(
            status="complete",
            original_message=req.message,
            gaps_detected=gap_texts,
            sources_used=combined,
            feynman_child=synthesis.for_child,
            feynman_expert=synthesis.for_expert,
            why_questions=why_result.get("questions", []),
            gf_id=gf_id
        )
        
    except Exception as e:
        logger.error(f"Ir à Escola error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scientific-compiler", response_model=ScientificCompilerResponse)
async def scientific_compiler(req: ScientificCompilerRequest):
    """Executa o Scientific Compiler."""
    logger.info(f"Scientific Compiler: {req.article_path}")
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        from app.services.scientific_compiler import ScientificCompiler
        
        compiler = ScientificCompiler()
        result = compiler.compile(req.article_path)
        
        return ScientificCompilerResponse(
            status="complete",
            article_title=result.get("article_title", "Unknown"),
            claims=result.get("claim_registry", []),
            evidence=result.get("evidence_registry", []),
            gmif_graph=result.get("gmif_graph", ""),
            lint_report=result.get("lint_report", []),
            critical_path=result.get("critical_path", []),
            fragility_analysis=result.get("fragility_analysis", {})
        )
        
    except Exception as e:
        logger.error(f"Scientific Compiler error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Grilo Falante API", "version": "1.0.0"}

# ============ CLI ============

if __name__ == "__main__":
    import uvicorn
    port = 8000
    if len(sys.argv) > 2 and sys.argv[1] == "--port":
        port = int(sys.argv[2])
    elif len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    
    uvicorn.run(app, host="0.0.0.0", port=port)