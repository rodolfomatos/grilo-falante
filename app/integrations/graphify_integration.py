"""
Integration layer: Graphify + GMIF + MemPalace

Orchestrates:
1. graphify: extract entities and relationships
2. GMIF: classify epistemic strength
3. MemPalace: persistent storage
"""

import json
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to use local modules
try:
    import sys
    sys.path.insert(0, "/home/rodolfo/src/epistemic-memory-architecture")
    from reasoning.gmif_graph_builder import GMIFGraphBuilder
    from reasoning.epistemic_graph import EpistemicGraph
    GMIF_AVAILABLE = True
except ImportError as e:
    logger.warning(f"GMIF module not available: {e}")
    GMIF_AVAILABLE = False


class GraphifyGMIFPipeline:
    """
    Integrated pipeline:
    1. Extract: graphify
    2. Classify: GMIF
    3. Store: MemPalace
    """
    
    def __init__(
        self,
        llm_provider: str = "ollama",  # ollama, iaedu, chatgpt
        llm_model: str = "llama3.2",
    ):
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.graphify_python = self._detect_graphify_python()
        
    def _detect_graphify_python(self) -> str:
        """Find graphify Python interpreter."""
        path = Path(".graphify_python")
        if path.exists():
            return path.read_text().strip()
        return "python3"
    
    def run_graphify(
        self,
        path: str,
        mode: str = "fast",
    ) -> Dict:
        """
        Run graphify extraction.
        
        Args:
            path: Directory or file to analyze
            mode: fast (AST only) or deep (+ semantic)
            
        Returns:
            Extraction result with nodes, edges
        """
        cmd = [
            self.graphify_python, "-c",
            f"""
import json
from pathlib import Path
from graphify.detect import detect
from graphify.extract import extract
from graphify.build import build_from_json

result = detect(Path('{path}'))
print(json.dumps(result))
"""
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                logger.error(f"graphify failed: {result.stderr}")
                return {"error": result.stderr}
                
            return json.loads(result.stdout)
        except Exception as e:
            logger.error(f"graphify error: {e}")
            return {"error": str(e)}
    
    def classify_with_gmif(
        self,
        nodes: List[Dict],
        edges: List[Dict],
    ) -> List[Dict]:
        """
        Classify nodes with GMIF.
        
        Uses heuristic based on edge types:
        - Premise nodes -> M1
        - Assumption nodes -> M2  
        - Claims with contradictions -> M4
        - Claims -> M5
        - Conclusions -> M7
        """
        if not GMIF_AVAILABLE:
            return self._classify_fallback(nodes, edges)
        
        # Build epistemic graph
        epistemic = EpistemicGraph()
        for node in nodes:
            epistemic.add_node(
                node["id"],
                node.get("label", ""),
                node.get("type", "claim"),
            )
        
        for edge in edges:
            epistemic.add_edge(
                edge["source"],
                edge["target"],
                edge.get("relation", "related"),
            )
        
        # Use GMIF builder
        builder = GMIFGraphBuilder(epistemic)
        gmif_graph = builder.build()
        
        # Annotate original nodes with GMIF
        annotated = []
        for node in nodes:
            gmif_type = gmif_graph.nodes.get(node.get("id"), {}).get("gmif_type", "M3")
            node["gmif_type"] = gmif_type
            node["gf_id"] = self._generate_gf_id(gmif_type, node.get("id", ""))
            annotated.append(node)
        
        return annotated
    
    def _classify_fallback(
        self,
        nodes: List[Dict],
        edges: List[Dict],
    ) -> List[Dict]:
        """
        Fallback GMIF classification without the module.
        
        Heuristics:
        - If node has EXTRACTED edges -> M1
        - If node has INFERRED edges only -> M5
        - If node has AMBIGUOUS edges -> M4
        - Otherwise -> M3
        """
        # Build edge type counts per node
        edge_types: Dict[str, Dict[str, int]] = {}
        for edge in edges:
            src = edge.get("source", "")
            tgt = edge.get("target", "")
            rel = edge.get("relation", "")
            conf = edge.get("confidence", "EXTRACTED")
            
            src = src or edge.get("source_file", "")
            tgt = tgt or edge.get("target_file", "")
            
            if src not in edge_types:
                edge_types[src] = {"EXTRACTED": 0, "INFERRED": 0, "AMBIGUOUS": 0}
            edge_types[src][conf] = edge_types[src].get(conf, 0) + 1
        
        annotated = []
        for node in nodes:
            node_id = node.get("id", "")
            types = edge_types.get(node_id, {})
            
            # Classify based on edge types
            if types.get("AMBIGUOUS", 0) > 0:
                gmif_type = "M4"
            elif types.get("EXTRACTED", 0) > 0:
                gmif_type = "M1"
            elif types.get("INFERRED", 0) > 0:
                gmif_type = "M5"
            else:
                gmif_type = "M3"  # No edges = partial
            
            node["gmif_type"] = gmif_type
            node["gf_id"] = self._generate_gf_id(gmif_type, node_id)
            annotated.append(node)
        
        return annotated
    
    def _generate_gf_id(self, gmif_type: str, node_id: str) -> str:
        """Generate GF-ID."""
        date = datetime.now().strftime("%y%m%d")
        short_hash = node_id[:6] if node_id else "empty"
        return f"GF-{date}-{gmif_type}-{short_hash}"
    
    def store_in_mempalace(
        self,
        nodes: List[Dict],
        edges: List[Dict],
        wing: str = "wing_grilo_falante",
    ) -> bool:
        """
        Store in MemPalace.
        
        Creates:
        - One room per community
        - Hall types based on GMIF
        """
        try:
            from mempalace.knowledge_graph import KnowledgeGraph
            from mempalace.searcher import search_memories
            
            kg = KnowledgeGraph()
            
            # Store nodes as facts
            for node in nodes:
                claim = node.get("label", node.get("text", ""))
                gmif = node.get("gmif_type", "M3")
                gf_id = node.get("gf_id", "")
                
                kg.add_triple(
                    gf_id,
                    "has_type",
                    gmif,
                    valid_from=datetime.now().isoformat(),
                )
                
                kg.add_triple(
                    gf_id,
                    "claim",
                    claim[:200],  # Limit length
                    valid_from=datetime.now().isoformat(),
                )
            
            # Store edges as relationships
            for edge in edges:
                src = edge.get("source", "")
                tgt = edge.get("target", "")
                rel = edge.get("relation", "")
                
                if src and tgt:
                    kg.add_triple(
                        src,
                        rel,
                        tgt,
                        valid_from=datetime.now().isoformat(),
                    )
            
            logger.info(f"Stored {len(nodes)} nodes in MemPalace")
            return True
            
        except ImportError:
            logger.warning("MemPalace not available - using fallback")
            return self._store_fallback(nodes, edges, wing)
        except Exception as e:
            logger.error(f"MemPalace storage failed: {e}")
            return self._store_fallback(nodes, edges, wing)
    
    def _store_fallback(
        self,
        nodes: List[Dict],
        edges: List[Dict],
        wing: str,
    ) -> bool:
        """Fallback JSON storage."""
        output_dir = Path("graphify-out")
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / "gmif_annotated.json"
        data = {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "wing": wing,
                "timestamp": datetime.now().isoformat(),
            }
        }
        
        output_file.write_text(json.dumps(data, indent=2))
        logger.info(f"Stored fallback: {output_file}")
        return True
    
    def run(
        self,
        path: str,
        store: bool = True,
    ) -> Dict:
        """
        Run full pipeline.
        
        Args:
            path: Directory to analyze
            store: Whether to store in MemPalace
            
        Returns:
            Annotated graph with GMIF and GF-IDs
        """
        logger.info(f"Starting pipeline on: {path}")
        
        # Step 1: Extract with graphify
        extraction = self.run_graphify(path)
        
        if "error" in extraction:
            return extraction
        
        # Load extraction result
        extract_file = Path(".graphify_extract.json")
        if extract_file.exists():
            data = json.loads(extract_file.read_text())
        else:
            return {"error": "No extraction result found"}
        
        nodes = data.get("nodes", [])
        edges = data.get("edges", [])
        
        logger.info(f"Extracted: {len(nodes)} nodes, {len(edges)} edges")
        
        # Step 2: Classify with GMIF
        classified_nodes = self.classify_with_gmif(nodes, edges)
        
        logger.info(f"Classified nodes: {sum(1 for n in classified_nodes if n.get('gmif_type') in ['M1', 'M5'])} high-confidence")
        
        # Step 3: Store in MemPalace
        if store:
            self.store_in_mempalace(classified_nodes, edges)
        
        return {
            "nodes": classified_nodes,
            "edges": edges,
            "metadata": {
                "source_path": path,
                "total_nodes": len(classified_nodes),
                "total_edges": len(edges),
            }
        }


def run_pipeline(
    path: str,
    llm_provider: str = "ollama",
) -> Dict:
    """Convenience function."""
    pipeline = GraphifyGMIFPipeline(llm_provider=llm_provider)
    return pipeline.run(path)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: graphify_integration.py <path>")
        sys.exit(1)
    
    result = run_pipeline(sys.argv[1])
    print(json.dumps(result, indent=2, default=str))