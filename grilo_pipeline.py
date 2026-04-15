#!/usr/bin/env python3
"""
Grilo Falante Pipeline - Full Version
====================================

Features:
- Timeout handling
- Retry logic
- Longer GF-IDs (12 chars)
- Cache support
- HTML export
- Human-in-the-loop verification
- Structured logging
- Dashboard

Usage: python3 grilo_pipeline.py <path> [options]

Options:
  --no-store         Skip storage
  --cache            Use cache
  --export-html      Export HTML visualization
  --verify-m4        Human verification of M4 claims
  --timeout N        Timeout (default: 60)
  --retry N          Retries (default: 3)
  --log FILE         Log to file
  --dashboard       Start dashboard
  --help, -h        Help
"""

import json
import sys
import os
import hashlib
import logging
import signal
import webbrowser
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from threading import Thread

# State machine
from state_machine import DotParser, StateMachine, load_graph, TransitionType
from loader_kernel import GriloLoaderKernel

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 60
DEFAULT_MAX_RETRIES = 3
GF_ID_LENGTH = 12
LOG_FILE = None


def set_log_file(filename):
    global LOG_FILE
    LOG_FILE = filename
    file_handler = logging.FileHandler(filename)
    file_handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(file_handler)
    logger.info("Logging to: " + filename)


class TimeoutError(Exception):
    pass


def install_timeout_handler(seconds):
    def timeout_handler(signum, frame):
        raise TimeoutError("Timeout")
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)


def remove_timeout_handler():
    signal.alarm(0)


def retry_operation(func, *args, max_retries=3, **kwargs):
    for attempt in range(1, max_retries + 1):
        try:
            return func(*args, **kwargs)
        except (TimeoutError, Exception) as e:
            if attempt < max_retries:
                logger.warning("Attempt " + str(attempt) + " failed: " + str(e))
            else:
                raise e


def generate_gf_id(gmif_type, node_id):
    content = node_id + ":" + datetime.now().isoformat()
    hash_part = hashlib.sha256(content.encode()).hexdigest()[:GF_ID_LENGTH]
    return "GF-" + datetime.now().strftime("%y%m%d") + "-" + gmif_type + "-" + hash_part


def load_from_cache(path):
    cache_dir = Path("graphify-out/.cache")
    if not cache_dir.exists():
        return None
    cache_file = cache_dir / (Path(path).name + ".json")
    if cache_file.exists():
        try:
            return json.loads(cache_file.read_text())
        except:
            pass
    return None


def save_to_cache(path, data):
    cache_dir = Path("graphify-out/.cache")
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / (Path(path).name + ".json")
    cache_file.write_text(json.dumps(data, indent=2))


def run_graphify(path, use_cache=False):
    try:
        import sys
        sys.path.insert(0, '/home/rodolfo/.local/lib/python3.10/site-packages')
        from graphify.detect import detect
        from graphify.extract import extract
        from graphify.build import build_from_json
    except ImportError as e:
        return {"error": "graphify not available: " + str(e)}

    if use_cache:
        cached = load_from_cache(path)
        if cached:
            logger.info("Using cache")
            return {"nodes": cached.get("nodes", []), "edges": cached.get("edges", [])}

    logger.info("Detecting: " + path)
    try:
        install_timeout_handler(DEFAULT_TIMEOUT)
        detection = detect(Path(path))
        remove_timeout_handler()
    except TimeoutError:
        remove_timeout_handler()
        return {"error": "Detection timed out"}

    logger.info("Files: " + str(detection.get("total_files", 0)))
    path_obj = Path(path)
    all_files = [f for f in (list(path_obj.glob("**/*")) if path_obj.is_dir() else [path_obj]) if f.is_file()]

    try:
        install_timeout_handler(DEFAULT_TIMEOUT)
        result = extract(all_files)
        remove_timeout_handler()
    except TimeoutError:
        remove_timeout_handler()
        return {"error": "Extraction timed out"}
    except Exception as e:
        remove_timeout_handler()
        return {"error": str(e)}

    logger.info("Building graph...")
    G = build_from_json(result)

    nodes = [{"id": n, "label": d.get("label", ""), "file_type": d.get("file_type", ""), 
             "source_file": d.get("source_file", "")} for n, d in G.nodes(data=True)]
    edges = [{"source": s, "target": t, "relation": d.get("relation", "related"),
              "confidence": d.get("confidence", "EXTRACTED")} for s, t, d in G.edges(data=True)]

    data = {"nodes": nodes, "edges": edges}
    if use_cache:
        save_to_cache(path, data)

    return data


def run_graphify_with_retry(path, use_cache=False):
    return retry_operation(run_graphify, path, use_cache=use_cache, max_retries=DEFAULT_MAX_RETRIES)


# ============================================================================
# LLM INTEGRATION (IAEDU)
# ============================================================================

def use_llm_for_classification(nodes, edges, llm_provider="iaedu"):
    """Use LLM for deeper semantic classification."""
    
    if llm_provider == "iaedu":
        try:
            sys.path.insert(0, str(Path(__file__).parent / "app" / "data" / "memory"))
            from llm_iaedu import IAEDUClient
            
            client = IAEDUClient()
            
            # Build concepts list
            concepts = [n.get("label", "") for n in nodes[:50]]
            
            prompt = f"""Analisa os seguintes conceitos e classifica cada um por força epistémica:

Conceitos:
{chr(10).join(f"- {c[:100]}" for c in concepts)}

Para cada conceito que parece factual mas não tem fontes explícitas, responde com formato:
CONCEITO: [nome] | TIPO: M3 | RAZÃO: [explicação curta]

Responde apenas com as linhas acima, em formato JSON se possível."""

            result = client.analyze_with_llm(nodes, prompt)
            logger.info("LLM classification done: " + str(result.get("concepts_analyzed", 0)))
            
            # Update nodes with new classifications (simplified)
            # In production, parse the response properly
            return nodes
            
        except ImportError:
            logger.warning("IAEDU module not found")
        except Exception as e:
            logger.warning("LLM classification failed: " + str(e))
    
    return nodes


def classify_gmif(nodes, edges):
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
        node["gf_id"] = generate_gf_id(gmif, node_id)
        node["verified"] = False  # For human verification

    return nodes


def verify_m4_claims(nodes):
    """Human verification of M4 (doubtful) claims."""
    m4_nodes = [n for n in nodes if n.get("gmif_type") == "M4"]
    
    if not m4_nodes:
        logger.info("No M4 claims to verify")
        return nodes
    
    print("\n=== HUMAN VERIFICATION REQUIRED ===")
    print("Found " + str(len(m4_nodes)) + " M4 (doubtful) claims:")
    
    for i, node in enumerate(m4_nodes[:10]):
        print("\n" + str(i+1) + ". " + node.get("gf_id", ""))
        print("   Label: " + node.get("label", "")[:80])
    
    print("\nEnter numbers to mark as verified (comma-separated), or press Enter to skip:")
    response = input("> ").strip()
    
    if response:
        try:
            indices = [int(x.strip()) - 1 for x in response.split(",")]
            for idx in indices:
                if 0 <= idx < len(m4_nodes):
                    m4_nodes[idx]["verified"] = True
                    logger.info("Verified: " + m4_nodes[idx].get("gf_id", ""))
        except ValueError:
            logger.warning("Invalid input, skipping verification")
    
    return nodes


def store_mempalace(nodes, edges):
    try:
        import sys
        sys.path.insert(0, '/home/rodolfo/.local/lib/python3.10/site-packages')
        from mempalace.knowledge_graph import KnowledgeGraph
        kg = KnowledgeGraph()

        for node in nodes:
            gf_id = node.get("gf_id", "")
            label = node.get("label", "")[:200]
            gmif = node.get("gmif_type", "M3")
            verified = node.get("verified", False)
            if gf_id:
                kg.add_triple(gf_id, "has_type", gmif)
                kg.add_triple(gf_id, "claim", label)
                if verified:
                    kg.add_triple(gf_id, "verified", "true")

        for edge in edges:
            src, tgt, rel = edge.get("source", ""), edge.get("target", ""), edge.get("relation", "")
            if src and tgt:
                kg.add_triple(src, rel, tgt)

        logger.info("Stored: " + str(len(nodes)))
        return {"status": "ok", "stored": len(nodes)}
    except Exception as e:
        logger.warning("MemPalace: " + str(e))
        output = {"nodes": nodes, "edges": edges, "metadata": {"timestamp": datetime.now().isoformat()}}
        Path("graphify-out/gmif_output.json").write_text(json.dumps(output, indent=2))
        logger.info("Saved: graphify-out/gmif_output.json")
        return {"status": "fallback", "stored": len(nodes)}


def export_html(nodes, edges, output_path="graphify-out/grilo_graph.html"):
    html = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Grilo Falante Dashboard</title>
<style>
body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;margin:0;padding:20px;background:#fafafa}
h1{color:#333;display:flex;align-items:center;gap:10px}
.badge{display:inline-block;padding:2px 8px;border-radius:4px;font-size:12px;color:#fff}
.badge-M1{background:#4CAF50}.badge-M2{background:#FFC107}.badge-M3{background:#FF9800}
.badge-M4{background:#F44336}.badge-M5{background:#8BC34A}.badge-M6{background:#03A9F4}.badge-M7{background:#9C27B0}
.stats{background:#fff;padding:20px;border-radius:8px;margin:20px 0;box-shadow:0 2px 4px rgba(0,0,0,0.1)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:15px;margin:20px 0}
.card{background:#fff;padding:15px;border-radius:8px;box-shadow:0 2px4px rgba(0,0,0,0.1)}
.verified{color:#4CAF50;font-weight:bold}
.warning{color:#F44336;font-weight:bold}
.search{padding:10px;border:2px solid #ddd;border-radius:8px;width:100%;font-size:16px}
</style></head>
<body>
<h1>📊 Grilo Falante Dashboard <button onclick="location.reload()">↻</button></h1>
<input class="search" id="search" placeholder="Search claims..." oninput="filter()">
<div class="stats">
<h3>Summary</h3>
<p>Total Nodes: <strong>""" + str(len(nodes)) + """</strong></p>
<p>Total Edges: <strong>""" + str(len(edges)) + """</strong></p>
</div>
<h3>By GMIF Type</h3>
<div class="grid">"""

    # Group by type
    by_type = {}
    for n in nodes:
        t = n.get("gmif_type", "M3")
        by_type[t] = by_type.get(t, 0) + 1

    for t, c in sorted(by_type.items()):
        html += """<div class="card"><span class="badge badge-""" + t + """">""" + t + """</span> = <strong>""" + str(c) + """</strong></div>"""

    html += """</div>
<h3>Claims (all)</h3>
<div class="grid" id="grid">"""

    for n in nodes:
        t = n.get("gmif_type", "M3")
        v = n.get("verified", False)
        label = n.get("label", "")[:100]
        html += """<div class="card" data-search=\"""" + label.lower() + """\">
<span class="badge badge-""" + t + """">""" + t + """</span>
""" + ("<span class='verified'>✓</span>" if v else "") + """
<br><small>""" + n.get("gf_id", "") + """</small>
<p>""" + label + """</p>
</div>"""

    html += """</div>
<script>
function filter(){
var q=document.getElementById("search").value.toLowerCase();
document.querySelectorAll(".card").forEach(function(c){
c.style.display=q&&c.dataset.search.indexOf(q)<0?"none":"block"});
}
</script>
</body></html>"""

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(html)
    logger.info("Exported: " + output_path)


def start_dashboard(path="graphify-out/grilo_graph.html"):
    try:
        webbrowser.open("file://" + os.path.abspath(path))
        logger.info("Dashboard opened in browser")
    except:
        logger.warning("Could not open browser")


def persist_blocked_output(payload):
    output_dir = Path(__file__).parent / "graphify-out"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "gmif_output.json"
    output_file.write_text(json.dumps(payload, indent=2))
    return output_file


def build_blocked_response(reason, message, details, context):
    payload = {
        "status": "blocked",
        "block": {
            "reason": reason,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat(),
        },
        "nodes": context.get("nodes", []),
        "edges": context.get("edges", []),
        "loader_kernel": context.get("loader_result", {}),
        "system_use_records": context.get("system_use_records", []),
    }
    output_file = persist_blocked_output(payload)
    logger.info("[BLOCK] Saved: " + str(output_file))
    return payload


def run(path, store=True, use_cache=False, export_html_flag=False, verify_m4=False, dashboard=False, llm_provider=None, state_machine_graph=None):
    # State machine execution if graph specified
    if state_machine_graph:
        return run_with_state_machine(path, state_machine_graph, store, use_cache, export_html_flag, verify_m4, dashboard, llm_provider)
    
    # Extract (with retry + cache)
    extraction = run_graphify_with_retry(path, use_cache)

    if "error" in extraction:
        return extraction

    nodes = extraction["nodes"]
    edges = extraction["edges"]
    logger.info("Extracted: " + str(len(nodes)) + " nodes, " + str(len(edges)) + " edges")

    # Classify (basic)
    classified = classify_gmif(nodes, edges)

    # LLM classification (if requested)
    if llm_provider:
        logger.info("Using LLM: " + llm_provider)
        classified = use_llm_for_classification(classified, edges, llm_provider)

    by_type = {}
    for n in classified:
        t = n.get("gmif_type", "M3")
        by_type[t] = by_type.get(t, 0) + 1

    logger.info("GMIF: " + str(by_type))

    if verify_m4:
        classified = verify_m4_claims(classified)

    if store:
        store_result = store_mempalace(classified, edges)
        logger.info("Storage: " + str(store_result))

    if export_html_flag:
        export_html(classified, edges)
        if dashboard:
            start_dashboard()

    return {"nodes": classified, "edges": edges, "stats": {"total": len(classified), "by_type": by_type}}


# ============================================================================
# STATE MACHINE INTEGRATION
# ============================================================================

def run_with_state_machine(path, graph_name, store=True, use_cache=False, export_html_flag=False, verify_m4=False, dashboard=False, llm_provider=None):
    """Execute pipeline with state machine governance."""
    
    logger.info("Loading state machine: " + graph_name)

    # Explicit regime activation via LOADER/KERNEL.
    loader_kernel = GriloLoaderKernel()
    load_result = loader_kernel.load("LOAD GriloFalante FROM system.md")
    if load_result.blocked:
        return build_blocked_response(
            reason=load_result.block_reason or "loader_blocked",
            message=load_result.error or "Loader blocked cycle",
            details=load_result.block_details or {},
            context={
                "path": path,
                "graph_name": graph_name,
                "loader_result": {
                    "system_name": load_result.system_name,
                    "system_path": load_result.system_path,
                    "loader_path": load_result.loader_path,
                    "kernel_path": load_result.kernel_path,
                    "authoritative_artefacts": load_result.authoritative_artefacts,
                },
                "system_use_records": list(load_result.use_records),
                "nodes": [],
                "edges": [],
            },
        )
    logger.info("Regime active via LOADER/KERNEL")
    
    # Load graph
    sm = load_graph(graph_name)
    
    logger.info("States: " + str(len(sm.states)))
    logger.info("Transitions: " + str(len(sm.transitions)))
    
    # Register handlers for each phase
    def handler_f0(input_data, context):
        """FASE 0: Context / Intention"""
        logger.info("[STATE F0] Intention / Context")
        # Context already available from path input
        context.setdefault("system_use_records", [])
        context["system_use_records"].append(
            loader_kernel.materialize_graph_use(graph_name, "F0", "F0->F1")
        )
        return {"phase": "F0", "context": path, "status": "continue"}
    
    def handler_f1(input_data, context):
        """FASE 1: Interpretation"""
        logger.info("[STATE F1] Interpretation")
        # Do extraction
        extraction = run_graphify_with_retry(context.get("path", ""), use_cache)
        if "error" in extraction:
            return {"phase": "F1", "status": "ERROR", "error": extraction.get("error")}
        context["nodes"] = extraction.get("nodes", [])
        context["edges"] = extraction.get("edges", [])
        logger.info("[F1] Extracted: " + str(len(context["nodes"])) + " nodes")
        context["system_use_records"].append(
            loader_kernel.materialize_graph_use(graph_name, "F1", "F1->F2")
        )
        return {"phase": "F1", "status": "continue"}
    
    def handler_f2(input_data, context):
        """FASE 2: Inference (Risk Zone)"""
        logger.info("[STATE F2] Inference (Risk Zone)")
        # Classify
        nodes = context.get("nodes", [])
        edges = context.get("edges", [])
        classified = classify_gmif(nodes, edges)
        
        # Set default LEGITIMACY_SUSPENDED for all nodes
        for node in classified:
            node["legitimacy"] = "LEGITIMACY_SUSPENDED"
        
        context["nodes"] = classified
        
        by_type = {}
        for n in classified:
            t = n.get("gmif_type", "M3")
            by_type[t] = by_type.get(t, 0) + 1
        logger.info("[F2] GMIF: " + str(by_type))
        logger.info("[F2] All claims set to LEGITIMACY_SUSPENDED")
        
        context["system_use_records"].append(
            loader_kernel.materialize_graph_use(graph_name, "F2", "F2->next")
        )
        return {"phase": "F2", "status": "continue", "gmif": by_type}
    
    def handler_f3(input_data, context):
        """FASE 3: Structuring"""
        logger.info("[STATE F3] Structuring")
        # LLM enhancement if requested
        if context.get("llm_provider"):
            nodes = context.get("nodes", [])
            edges = context.get("edges", [])
            classified = use_llm_for_classification(nodes, edges, context["llm_provider"])
            context["nodes"] = classified
        return {"phase": "F3", "status": "continue"}
    
    def handler_f4(input_data, context):
        """FASE 4: Cognitive LINT"""
        logger.info("[STATE F4] Cognitive LINT")
        nodes = context.get("nodes", [])
        
        # Count M4 (doubtful) claims
        m4_count = sum(1 for n in nodes if n.get("gmif_type") == "M4")
        
        if m4_count > 0:
            logger.warning("[F4] WARNING: " + str(m4_count) + " M4 claims detected")
            # If verify_m4, do human verification
            if context.get("verify_m4"):
                verified = verify_m4_claims(nodes)
                context["nodes"] = verified
                m4_count = sum(1 for n in verified if n.get("gmif_type") == "M4" and not n.get("verified", False))
        
        # If many M4, suggest REJECT
        if m4_count > len(nodes) * 0.5:
            return {"phase": "F4", "status": "REJECT", "reason": "Too many M4 claims"}
        
        return {"phase": "F4", "status": "ACCEPT"}
    
    def handler_f5(input_data, context):
        """FASE 5: Re-execution"""
        logger.info("[STATE F5] Re-execution")
        # This would re-do F1-F3 with different parameters
        return {"phase": "F5", "status": "REEXECUTE"}
    
    def handler_f6(input_data, context):
        """FASE 6: Human Validation"""
        logger.info("[STATE F6] Human Validation")
        nodes = context.get("nodes", [])
        
        # Count current legitimacy states
        suspended = sum(1 for n in nodes if n.get("legitimacy") == "LEGITIMACY_SUSPENDED")
        asserted = sum(1 for n in nodes if n.get("legitimacy") == "LEGITIMACY_ASSERTED")
        
        logger.info(f"[F6] LEGITIMACY_SUSPENDED: {suspended}, LEGITIMACY_ASSERTED: {asserted}")
        
        # If verify_m4, allow human to assert legitimacy
        if context.get("verify_m4"):
            m1_nodes = [n for n in nodes if n.get("gmif_type") == "M1"]
            logger.info(f"[F6] {len(m1_nodes)} M1 claims available for human assertion")
            
            # In a full implementation, this would prompt human to assert
            # For now, auto-assert M1 claims
            for n in m1_nodes:
                n["legitimacy"] = "LEGITIMACY_ASSERTED"
            
            asserted_after = sum(1 for n in nodes if n.get("legitimacy") == "LEGITIMACY_ASSERTED")
            logger.info(f"[F6] After validation: {asserted_after} LEGITIMACY_ASSERTED")
        
        # Store results
        if context.get("store"):
            edges = context.get("edges", [])
            store_result = store_mempalace(nodes, edges)
            logger.info("[F6] Storage: " + str(store_result))
        
        return {"phase": "F6", "status": "continue", "legitimacy_asserted": sum(1 for n in nodes if n.get("legitimacy") == "LEGITIMACY_ASSERTED")}
    
    def handler_f7(input_data, context):
        """FASE 7: Promotion Gate"""
        logger.info("[STATE F7] Promotion Gate")
        # Determine if promote or block
        nodes = context.get("nodes", [])
        
        # Check criteria
        m1_count = sum(1 for n in nodes if n.get("gmif_type") == "M1")
        m4_unverified = sum(1 for n in nodes if n.get("gmif_type") == "M4" and not n.get("verified", False))
        
        # NEW: Check legitimacy - need at least some ASSERTED
        legitimacy_asserted = sum(1 for n in nodes if n.get("legitimacy") == "LEGITIMACY_ASSERTED")
        legitimacy_suspended = sum(1 for n in nodes if n.get("legitimacy") == "LEGITIMACY_SUSPENDED")
        
        logger.info(f"[F7] M1: {m1_count}, M4 unverified: {m4_unverified}")
        logger.info(f"[F7] LEGITIMACY_ASSERTED: {legitimacy_asserted}, LEGITIMACY_SUSPENDED: {legitimacy_suspended}")
        
        if m4_unverified > 0:
            logger.warning("[F7] BLOCKING: unverified M4 claims")
            return {
                "phase": "F7",
                "status": "BLOCK",
                "block_reason": "unverified_m4_claims",
                "block_message": "Promotion blocked because contradictory claims remain unverified.",
                "block_details": {"m4_unverified": m4_unverified},
            }
        
        if m1_count == 0:
            logger.warning("[F7] BLOCKING: no M1 claims")
            return {
                "phase": "F7",
                "status": "BLOCK",
                "block_reason": "no_m1_claims",
                "block_message": "Promotion blocked because no grounded M1 claims were found.",
                "block_details": {"m1_count": m1_count},
            }
        
        if legitimacy_asserted == 0:
            logger.warning("[F7] BLOCKING: no LEGITIMACY_ASSERTED claims")
            return {
                "phase": "F7",
                "status": "BLOCK",
                "block_reason": "no_legitimacy_asserted",
                "block_message": "Promotion blocked because no claim has explicit asserted legitimacy.",
                "block_details": {"legitimacy_asserted": legitimacy_asserted},
            }
        
        logger.info("[F7] PROMOTING")
        return {"phase": "F7", "status": "PROMOTE"}
    
    def persist_governed_output(context):
        nodes = context.get("nodes", [])
        edges = context.get("edges", [])
        
        # Export HTML if requested
        if context.get("export_html"):
            export_html(nodes, edges)
            if context.get("dashboard"):
                start_dashboard()
        
        # Save final output with legitimacy info
        output_dir = Path(__file__).parent / "graphify-out"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Add metadata
        suspended = sum(1 for n in nodes if n.get("legitimacy") == "LEGITIMACY_SUSPENDED")
        asserted = sum(1 for n in nodes if n.get("legitimacy") == "LEGITIMACY_ASSERTED")
        
        output = {
            "status": "promoted",
            "nodes": nodes, 
            "edges": edges, 
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "legitimacy_suspended": suspended,
                "legitimacy_asserted": asserted,
                "total": len(nodes)
            },
            "loader_kernel": context.get("loader_result", {}),
            "system_use_records": context.get("system_use_records", [])
        }
        
        output_file = output_dir / "gmif_output.json"
        output_file.write_text(json.dumps(output, indent=2))
        return output_file

    def handler_f8(input_data, context):
        """FASE 8: Persistence"""
        logger.info("[STATE F8] Persistence")
        nodes = context.get("nodes", [])
        output_file = persist_governed_output(context)
        logger.info("[F8] Saved: " + str(output_file))
        
        return {"phase": "F8", "status": "DONE", "nodes": len(nodes)}
    
    # Register handlers
    sm.set_handler("F_M1", lambda d, c: {"phase": "F_M1", "status": "continue"})
    sm.set_handler("ARTIFACTS", lambda d, c: {"phase": "ARTIFACTS", "status": "continue"})
    sm.set_handler("F0", handler_f0)
    sm.set_handler("F1", handler_f1)
    sm.set_handler("F15", lambda d, c: logger.info("[STATE F15] Claim Classification") or {"phase": "F15", "status": "continue"})
    sm.set_handler("F2", handler_f2)
    sm.set_handler("EXPLORATION_CONTROL", lambda d, c: {"phase": "EXPLORATION_CONTROL", "status": "continue"})
    sm.set_handler("F3", handler_f3)
    sm.set_handler("F4", handler_f4)
    sm.set_handler("VALIDATION_QUEUE", lambda d, c: {"phase": "VALIDATION_QUEUE", "status": "continue"})
    sm.set_handler("VALIDATION_TIERS", lambda d, c: {"phase": "VALIDATION_TIERS", "status": "continue"})
    sm.set_handler("F5", handler_f5)
    sm.set_handler("F6", handler_f6)
    sm.set_handler("EVIDENCE", lambda d, c: {"phase": "EVIDENCE", "status": "continue"})
    sm.set_handler("VERIFY", lambda d, c: {"phase": "VERIFY", "status": "continue"})
    sm.set_handler("CONFIDENCE", lambda d, c: {"phase": "CONFIDENCE", "status": "continue"})
    sm.set_handler("F7", handler_f7)
    sm.set_handler("F8", handler_f8)
    
    # Governance states (g8)
    def handler_acordar(input_data, context):
        """ACORDAR: Bootstrap / Anchoring ritual."""
        logger.info("[STATE ACORDAR] Bootstrap / Anchoring")
        
        # Get or request temporal anchoring + intention
        temporal = context.get("temporal_anchoring")
        intention = context.get("intention")
        
        if not temporal:
            # Use current time as default
            temporal = datetime.now().isoformat()
            context["temporal_anchoring"] = temporal
            logger.info(f"[ACORDAR] Temporal anchoring: {temporal}")
        
        if not intention:
            # Use path as default intention
            intention = f"Analisar {context.get('path', 'input')}"
            context["intention"] = intention
            logger.info(f"[ACORDAR] Intention: {intention}")
        
        return {"phase": "ACORDAR", "status": "continue", "temporal": temporal, "intention": intention}
    
    sm.set_handler("ACORDAR", handler_acordar)
    sm.set_handler("USER", lambda d, c: {"phase": "USER", "status": "continue"})
    sm.set_handler("DIGITAL_OBJECT", lambda d, c: {"phase": "DIGITAL_OBJECT", "status": "continue"})
    sm.set_handler("GATES", lambda d, c: logger.info("[STATE GATES] Normative Gates") or {"phase": "GATES", "status": "continue", "next": "F_M1"})
    sm.set_handler("LEDGER", lambda d, c: {"phase": "LEDGER", "status": "continue"})
    sm.set_handler("CAPSULES", lambda d, c: {"phase": "CAPSULES", "status": "continue"})
    sm.set_handler("DOCUMENTS", lambda d, c: {"phase": "DOCUMENTS", "status": "continue"})
    sm.set_handler("PARADIGM_MAP", lambda d, c: {"phase": "PARADIGM_MAP", "status": "continue"})
    sm.set_handler("ANOMALY_BUFFER", lambda d, c: {"phase": "ANOMALY_BUFFER", "status": "continue"})
    sm.set_handler("FOUNDATION_AUDIT", lambda d, c: {"phase": "FOUNDATION_AUDIT", "status": "continue"})
    sm.set_handler("DRIFT_AUDIT", lambda d, c: {"phase": "DRIFT_AUDIT", "status": "continue"})
    sm.set_handler("LINEAGE", lambda d, c: {"phase": "LINEAGE", "status": "continue"})
    sm.set_handler("GROUND", lambda d, c: {"phase": "GROUND", "status": "continue"})
    sm.set_handler("DERIVED", lambda d, c: {"phase": "DERIVED", "status": "continue"})
    sm.set_handler("HYPOTHESIS", lambda d, c: {"phase": "HYPOTHESIS", "status": "continue"})
    
    # Cognitive modes (MEX, MEXS, AUDIT, MULTI, MTS)
    sm.set_handler("MEX", lambda d, c: logger.info("[MODE MEX] Free Exploration") or {"phase": "MEX", "status": "continue"})
    sm.set_handler("MEXS", lambda d, c: logger.info("[MODE MEX-S] Structured Exploration") or {"phase": "MEXS", "status": "continue"})
    sm.set_handler("AUDIT", lambda d, c: logger.info("[MODE A] Hostile Audit") or {"phase": "AUDIT", "status": "continue"})
    sm.set_handler("MULTI", lambda d, c: logger.info("[MODE D] Multi-Agent") or {"phase": "MULTI", "status": "continue"})
    sm.set_handler("MTS", lambda d, c: logger.info("[MODE MTS] Simulated Terminal") or {"phase": "MTS", "status": "continue"})
    sm.set_handler("Regime", lambda d, c: logger.info("[STATE Regime] Governance") or {"phase": "Regime", "status": "continue"})
    sm.set_handler("Artifacts", lambda d, c: logger.info("[STATE Artifacts]") or {"phase": "Artifacts", "status": "continue"})
    
    # Build context from parameters
    exec_context = {
        "path": path,
        "store": store,
        "use_cache": use_cache,
        "export_html": export_html_flag,
        "verify_m4": verify_m4,
        "dashboard": dashboard,
        "llm_provider": llm_provider,
        "intention": intention,
        "temporal_anchoring": temporal_anchoring,
        "loader_result": {
            "system_name": load_result.system_name,
            "system_path": load_result.system_path,
            "loader_path": load_result.loader_path,
            "kernel_path": load_result.kernel_path,
            "authoritative_artefacts": load_result.authoritative_artefacts,
        },
        "system_use_records": list(load_result.use_records),
        "nodes": [],
        "edges": []
    }
    
    # Start state machine.
    # g8 works best from F_M1; g7/g9 can use their natural entry.
    start_state = "F_M1" if graph_name == "g8_grilo_falante_unified_cognitive_model" else None
    sm.start(start_state)
    logger.info("Started at: " + sm.current_state)
    
    # Run until blocked or max steps
    max_steps = 50
    step = 0
    while step < max_steps:
        result = sm.step(None, exec_context)
        
        logger.info("[STEP " + str(step) + "] State: " + result.current_state)
        
        if result.accepted:
            logger.info("→ ACCEPTED")
        elif result.rejected:
            logger.info("→ REJECTED")
        elif result.blocked:
            logger.info("→ BLOCKED")
            if isinstance(result.output, dict):
                return build_blocked_response(
                    reason=result.output.get("block_reason", "blocked_transition"),
                    message=result.output.get("block_message", "Cycle blocked by governance rules."),
                    details=result.output.get("block_details", {}),
                    context=exec_context,
                )
            return build_blocked_response(
                reason="blocked_transition",
                message="Cycle blocked by governance rules.",
                details={"state": result.current_state},
                context=exec_context,
            )

        if result.current_state == "F8":
            output_file = persist_governed_output(exec_context)
            logger.info("[F8] Saved: " + str(output_file))
            logger.info("[COMPLETE] F8 reached - persistence done")
            break
        
        step += 1
    
    # Return result
    nodes = exec_context.get("nodes", [])
    by_type = {}
    for n in nodes:
        t = n.get("gmif_type", "M3")
        by_type[t] = by_type.get(t, 0) + 1
    
    # Legitimacy stats
    legitimacy_asserted = sum(1 for n in nodes if n.get("legitimacy") == "LEGITIMACY_ASSERTED")
    legitimacy_suspended = sum(1 for n in nodes if n.get("legitimacy") == "LEGITIMACY_SUSPENDED")
    
    return {
        "status": "promoted",
        "nodes": nodes,
        "edges": exec_context.get("edges", []),
        "stats": {
            "total": len(nodes), 
            "by_type": by_type,
            "legitimacy_asserted": legitimacy_asserted,
            "legitimacy_suspended": legitimacy_suspended
        },
        "state_machine": {"history": result.history},
        "loader_kernel": exec_context.get("loader_result", {}),
        "system_use_records": exec_context.get("system_use_records", [])
    }


def print_help():
    print("""
Grilo Falante Pipeline - Full Version
======================================

Features: Timeout, Retry, Cache, HTML, Human Verify, Log, Dashboard, LLM, State Machine

Usage: python3 grilo_pipeline.py <path> [options]

Options:
  --no-store         Skip storage
  --cache            Use cache
  --export-html      Export HTML dashboard
  --verify-m4        Human verification of M4 claims
  --llm PROVIDER    Use LLM for analysis (iaedu, openai, ollama)
  --graph NAME       Use state machine graph (e.g., g7_grilo_falante_cognitive_model_v7)
  --intention TEXT   Set intention for ACORDAR ritual
  --temporal DATE    Set temporal anchoring for ACORDAR (ISO format)
  --log FILE         Log to file
  --dashboard       Open dashboard in browser
  --timeout N        Timeout (default: 60)
  --retry N          Retries (default: 3)
  --help, -h         Help

Examples:
  python3 grilo_pipeline.py ./src
  python3 grilo_pipeline.py ./docs --cache --export-html --dashboard
  python3 grilo_pipeline.py ./app --verify-m4 --llm iaedu
  python3 grilo_pipeline.py ./project --graph g8_grilo_falante_unified_cognitive_model --intention "Analisar segurança"
""")
    sys.exit(0)


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args or "-h" in args or "--help" in args:
        print_help()

    # Parse args - find first non-option as path
    path = None
    store = True
    use_cache = False
    do_export = False
    verify_m4 = False
    dashboard = False
    llm_provider = None
    state_machine_graph = None
    intention = None
    temporal_anchoring = None
    
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--no-store":
            store = False
        elif arg == "--cache":
            use_cache = True
        elif arg == "--export-html":
            do_export = True
        elif arg == "--verify-m4":
            verify_m4 = True
        elif arg == "--dashboard":
            do_export = True
            dashboard = True
        elif arg == "--graph" and i + 1 < len(args):
            state_machine_graph = args[i + 1]
            i += 1
        elif arg == "--intention" and i + 1 < len(args):
            intention = args[i + 1]
            i += 1
        elif arg == "--temporal" and i + 1 < len(args):
            temporal_anchoring = args[i + 1]
            i += 1
        elif arg == "--timeout" and i + 1 < len(args):
            try:
                DEFAULT_TIMEOUT = int(args[i + 1])
                i += 1
            except ValueError:
                logger.warning(f"Invalid timeout value: {args[i + 1]}")
        elif arg == "--retry" and i + 1 < len(args):
            try:
                DEFAULT_MAX_RETRIES = int(args[i + 1])
                i += 1
            except ValueError:
                logger.warning(f"Invalid retry value: {args[i + 1]}")
        elif arg == "--log" and i + 1 < len(args):
            set_log_file(args[i + 1])
            i += 1
        elif arg == "--llm" and i + 1 < len(args):
            llm_provider = args[i + 1]
            i += 1
        elif not arg.startswith("-"):
            # First non-option is path
            if path is None:
                path = arg
        i += 1

    if not path:
        print("Error: No path specified")
        sys.exit(1)

    logger.info("=== Grilo Falante Pipeline ===")
    logger.info("Path: " + path)
    logger.info("Timeout: " + str(DEFAULT_TIMEOUT) + "s")
    logger.info("Retries: " + str(DEFAULT_MAX_RETRIES))
    if state_machine_graph:
        logger.info("State Machine: " + state_machine_graph)
    if llm_provider:
        logger.info("LLM: " + llm_provider)

    result = run(path, store, use_cache, do_export, verify_m4, dashboard, llm_provider, state_machine_graph)

    if "error" in result:
        print("\nERROR: " + result["error"])
        sys.exit(1)

    print("\n✓ Done!")
    print("Output: graphify-out/gmif_output.json")
    if do_export:
        print("HTML: graphify-out/grilo_graph.html")
        print("Dashboard: Open in browser or file://" + os.path.abspath("graphify-out/grilo_graph.html"))
    print("\nGF-IDs (example):")
    for n in result["nodes"][:3]:
        v = " ✓" if n.get("verified", False) else ""
        print("  " + n.get("gf_id", "") + v + ": " + n.get("label", "")[:40])
