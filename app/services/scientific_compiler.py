#!/usr/bin/env python3
"""
Scientific Compiler — Stage 1-12 Implementation

Implementa o gf_scientific_compiler_v_2_spec.md:
- Stage 1: GF Initialization
- Stage 2: Article Ingestion
- Stage 3: Citation Verification
- Stage 4: Shadow Document Acquisition
- Stage 5: Claim Extraction
- Stage 6: Evidence Extraction
- Stage 7: GMIF Classification
- Stage 8: Graph Construction
- Stage 9: Graph Lint
- Stage 10: Critical Path
- Stage 11: Fragility Analysis
- Stage 12: Compilation Report

Autor: Rodolfo
Data: 2026-04-13
"""

import json
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class Claim:
    """Uma claim extraída do artigo."""
    id: str
    section: str
    text: str
    claim_type: str  # "empirical", "normative", "architectural"
    gmif_type: str = "M3"  # default
    
@dataclass
class Evidence:
    """Uma evidência."""
    id: str
    source: str  # reference ID
    text: str
    gmif_type: str = "M3"
    verified: bool = False
    
@dataclass
class ShadowDocument:
    """Shadow document de uma referência."""
    ref_id: str
    metadata: Dict
    claims: List[str]
    reliability: str = "M3"  # default
    
@dataclass
class CompilationReport:
    """Resultado final da compilação."""
    article_title: str
    claim_registry: List[Dict]
    evidence_registry: List[Dict]
    shadow_index: List[Dict]
    gmif_graph: str
    lint_report: List[str]
    critical_path: List[str]
    fragility_analysis: Dict
    timestamp: str


# ============================================================================
# STAGE 1: GF INITIALIZATION
# ============================================================================

class GFInitialization:
    """
    Stage 1: GF Initialisation
    
    Estabelece regras epistémicas:
    - inference must be evidence-grounded
    - citations must correspond to shadow documents
    - unsupported reasoning must be flagged
    """
    
    def __init__(self):
        self.rules = {
            "evidence_grounded": True,
            "citation_required": True,
            "unsupported_flagged": True
        }
        self.active = True
        
    def initialize(self) -> Dict:
        logger.info("Stage 1: GF Initialization")
        return {
            "status": "active",
            "rules": self.rules,
            "timestamp": datetime.now().isoformat()
        }


# ============================================================================
# STAGE 2: ARTICLE INGESTION
# ============================================================================

class ArticleIngestion:
    """
    Stage 2: Article Ingestion
    
    Parse do artigo.
    Extracted: sections, claims, citations, bibliography
    """
    
    def __init__(self):
        self.sections = []
        self.citations = []
        self.bibliography = []
        
    def ingest_file(self, filepath: str) -> Dict:
        """Ingere artigo de ficheiro."""
        logger.info(f"Stage 2: Article Ingestion - {filepath}")
        
        path = Path(filepath)
        if not path.exists():
            return {"error": f"File not found: {filepath}"}
        
        content = path.read_text(encoding='utf-8', errors='ignore')
        
        # Extract sections (headers)
        self.sections = self._extract_sections(content)
        
        # Extract citations
        self.citations = self._extract_citations(content)
        
        # Extract bibliography
        self.bibliography = self._extract_bibliography(content)
        
        return {
            "title": self._extract_title(content),
            "sections": len(self.sections),
            "citations": len(self.citations),
            "references": len(self.bibliography)
        }
    
    def _extract_title(self, content: str) -> str:
        lines = content.split('\n')
        for line in lines:
            if line.strip().startswith('# '):
                return line.strip('# ').strip()
        return "Unknown"
    
    def _extract_sections(self, content: str) -> List[str]:
        sections = []
        for line in content.split('\n'):
            if line.startswith('#'):
                sections.append(line.strip('# ').strip())
        return sections
    
    def _extract_citations(self, content: str) -> List[str]:
        # Look for [...] or (Author, Year)
        citations = re.findall(r'\[(\d+)\]|\(([A-Z][a-z]+,?\s*\d{4})', content)
        return [c[0] or c[1] for c in citations]
    
    def _extract_bibliography(self, content: str) -> List[Dict]:
        refs = []
        in_refs = False
        for line in content.split('\n'):
            if 'bibliografia' in line.lower() or 'references' in line.lower():
                in_refs = True
                continue
            if in_refs and line.strip():
                if line[0].isdigit():
                    refs.append(line.strip())
        return refs


# ============================================================================
# STAGE 3: CITATION VERIFICATION
# ============================================================================

class CitationVerification:
    """
    Stage 3: Citation Verification
    
    Check cada citação contra shadow corpus.
    """
    
    def __init__(self, shadow_corpus_path: str = None):
        self.shadow_corpus_path = shadow_corpus_path
        self.verified = []
        self.missing = []
        self.unverifiable = []
        
    def verify(self, citations: List[str], shadow_docs: Dict) -> Dict:
        logger.info("Stage 3: Citation Verification")
        
        for cite in citations:
            if cite in shadow_docs:
                self.verified.append(cite)
            elif "placeholder" in shadow_docs:
                self.missing.append(cite)
            else:
                self.unverifiable.append(cite)
        
        return {
            "verified": self.verified,
            "missing": self.missing,
            "unverifiable": self.unverifiable
        }


# ============================================================================
# STAGE 4: SHADOW DOCUMENT ACQUISITION
# ============================================================================

class ShadowDocumentAcquisition:
    """
    Stage 4: Shadow Document Acquisition
    
    Converte referências em shadow documents.
    """
    
    def __init__(self):
        self.shadows = {}
        
    def acquire(self, reference: str) -> ShadowDocument:
        """Cria shadow document para uma referência."""
        shadow = ShadowDocument(
            ref_id=reference,
            metadata={"title": reference},
            claims=[],
            reliability="M4"  # default: unverified
        )
        self.shadows[reference] = shadow
        return shadow
    
    def get_shadows(self) -> List[ShadowDocument]:
        return list(self.shadows.values())


# ============================================================================
# STAGE 5: CLAIM EXTRACTION
# ============================================================================

class ClaimExtraction:
    """
    Stage 5: Claim Extraction
    
    Extrai claims e atribui IDs.
    """
    
    def __init__(self):
        self.claims = []
        self.counter = 0
        
    def extract(self, content: str) -> List[Claim]:
        logger.info("Stage 5: Claim Extraction")
        
        self.claims = []
        self.counter = 0
        
        # Simple claim patterns
        patterns = [
            (r"We\s+show\s+that\s+(.+?)\.", "empirical"),
            (r"We\s+propose\s+(.+?)\.", "architectural"),
            (r"We\s+argue\s+that\s+(.+?)\.", "normative"),
            (r"Results\s+(?:show|indicate|suggest)\s+(.+?)\.", "empirical"),
            (r"This\s+suggests\s+(.+?)\.", "normative"),
        ]
        
        for pattern, claim_type in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                self.counter += 1
                claim = Claim(
                    id=f"C{self.counter}",
                    section="unknown",
                    text=match.group(1).strip()[:100],
                    claim_type=claim_type,
                    gmif_type="M5"  # default interpretation
                )
                self.claims.append(claim)
        
        # Limitar a 20 claims
        self.claims = self.claims[:20]
        
        return self.claims


# ============================================================================
# STAGE 6: EVIDENCE EXTRACTION
# ============================================================================

class EvidenceExtraction:
    """
    Stage 6: Evidence Extraction
    
    Extrai itens de evidência.
    """
    
    def __init__(self):
        self.evidence = []
        self.counter = 0
        
    def extract(self, content: str, citations: List[str]) -> List[Evidence]:
        logger.info("Stage 6: Evidence Extraction")
        
        self.evidence = []
        self.counter = 0
        
        # Look for evidence indicators
        evidence_patterns = [
            r"(?:Table|Figure|Fig\.)\s*(\d+)",
            r"data\s+(?:show|indicate|suggest)",
            r"according\s+to\s+([A-Z][a-z]+)",
            r"prior\s+work\s+has\s+shown",
        ]
        
        for pattern in evidence_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                self.counter += 1
                ev = Evidence(
                    id=f"E{self.counter}",
                    source=citations[0] if citations else "unknown",
                    text=match.group(0),
                    gmif_type="M1",  # default primary
                    verified=False
                )
                self.evidence.append(ev)
        
        return self.evidence[:20]


# ============================================================================
# STAGE 7: GMIF CLASSIFICATION
# ============================================================================

class GMIFClassification:
    """
    Stage 7: GMIF Classification
    
    Classifica evidência usando GMIF taxonomy.
    """
    
    GMIF_MAP = {
        "empirical": "M1",  # Primary empirical data
        "normative": "M5",   # Interpretation
        "architectural": "M6", # Derived
        "unverified": "M4",   # Doubtful testimony
    }
    
    COLORS = {
        "M1": "green",
        "M2": "yellow", 
        "M3": "orange",
        "M4": "red",
        "M5": "yellow",
        "M6": "orange",
        "M7": "yellow"
    }
    
    @classmethod
    def classify(cls, claim: Claim) -> str:
        return cls.GMIF_MAP.get(claim.claim_type, "M3")
    
    @classmethod
    def get_color(cls, gmif_type: str) -> str:
        return cls.COLORS.get(gmif_type, "white")


# ============================================================================
# STAGE 8: GRAPH CONSTRUCTION
# ============================================================================

class GraphConstruction:
    """
    Stage 8: Epistemic Graph Construction
    
    Constrói grafo GMIF em formato DOT.
    """
    
    def __init__(self):
        self.nodes = []
        self.edges = []
        
    def build(self, claims: List[Claim], evidence: List[Evidence]) -> str:
        logger.info("Stage 8: Graph Construction")
        
        dot = 'digraph EpistemicGraph {\n'
        dot += 'node [style=filled];\n\n'
        
        # Evidence nodes
        for e in evidence:
            color = GMIFClassification.get_color(e.gmif_type)
            dot += f'{e.id} [label="{e.gmif_type}: {e.text[:30]}...", fillcolor="{color}"];\n'
        
        # Claim nodes
        for c in claims:
            color = GMIFClassification.get_color(c.gmif_type)
            shape = "ellipse" if c.gmif_type in ["M5", "M6", "M7"] else "box"
            dot += f'{c.id} [label="{c.gmif_type}: {c.text[:30]}...", fillcolor="{color}", shape="{shape}"];\n'
        
        # Edges: evidence -> claims
        for i, e in enumerate(evidence[:len(claims)]):
            dot += f'{e.id} -> {claims[i].id};\n'
        
        dot += '}\n'
        
        return dot


# ============================================================================
# STAGE 9: GRAPH LINT
# ============================================================================

class GraphLint:
    """
    Stage 9: GMIF Graph Lint
    
    Verifica integridade estrutural.
    """
    
    RULES = ["L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8"]
    
    def __init__(self):
        self.errors = []
        
    def lint(self, dot_graph: str, claims: List[Claim], evidence: List[Evidence]) -> List[str]:
        logger.info("Stage 9: Graph Lint")
        
        self.errors = []
        
        # L1: Orphan node detection
        claim_ids = {c.id for c in claims}
        evidence_ids = {e.id for e in evidence}
        all_ids = claim_ids | evidence_ids
        
        for node_id in all_ids:
            if node_id not in dot_graph:
                self.errors.append(f"L1: Orphan node {node_id}")
        
        # L2: Evidence reachability
        if evidence and not claims:
            self.errors.append("L2: No evidence reaching claims")
        
        # L3: Conclusion grounding
        if not evidence:
            self.errors.append("L3: No conclusion grounding")
        
        return self.errors


# ============================================================================
# STAGE 10: CRITICAL PATH COMPUTATION
# ============================================================================

class CriticalPathComputation:
    """
    Stage 10: Critical Path Computation
    
    Identifica a cadeia mínima de raciocínio.
    """
    
    def compute(self, claims: List[Claim], evidence: List[Evidence]) -> List[str]:
        logger.info("Stage 10: Critical Path Computation")
        
        path = []
        
        # Simple: evidência mais próxima da primeira claim
        if evidence and claims:
            path = [evidence[0].id, "->", claims[0].id]
        
        return [">".join(path)] if path else ["No path"]


# ============================================================================
# STAGE 11: FRAGILITY ANALYSIS
# ============================================================================

class FragilityAnalysis:
    """
    Stage 11: Fragility Analysis
    
    Analisa o grafo para:
    - single-points of failure
    - unsupported reasoning
    - weak evidence dependencies
    """
    
    def analyze(self, claims: List[Claim], evidence: List[Evidence], errors: List[str]) -> Dict:
        logger.info("Stage 11: Fragility Analysis")
        
        single_point_failure = []
        weak_evidence = []
        
        # Check for single evidence support
        for c in claims:
            supporting = [e for e in evidence]
            if len(supporting) == 1:
                single_point_failure.append(c.id)
        
        # Check for unverified evidence
        for e in evidence:
            if not e.verified:
                weak_evidence.append(e.id)
        
        return {
            "single_point_failure": single_point_failure,
            "weak_evidence": weak_evidence,
            "lint_errors": len(errors),
            "fragility_score": len(single_point_failure) + len(weak_evidence)
        }


# ============================================================================
# STAGE 12: COMPILATION REPORT
# ============================================================================

class CompilationReportGenerator:
    """
    Stage 12: Compilation Report
    
    Gera relatório final.
    """
    
    def generate(
        self,
        title: str,
        claims: List[Claim],
        evidence: List[Evidence],
        shadows: List[ShadowDocument],
        dot_graph: str,
        lint_errors: List[str],
        critical_path: List[str],
        fragility: Dict
    ) -> CompilationReport:
        logger.info("Stage 12: Compilation Report")
        
        return CompilationReport(
            article_title=title,
            claim_registry=[asdict(c) for c in claims],
            evidence_registry=[asdict(e) for e in evidence],
            shadow_index=[asdict(s) for s in shadows],
            gmif_graph=dot_graph,
            lint_report=lint_errors,
            critical_path=critical_path,
            fragility_analysis=fragility,
            timestamp=datetime.now().isoformat()
        )


# ============================================================================
# SCIENTIFIC COMPILER ORCHESTRATOR
# ============================================================================

class ScientificCompiler:
    """
    Orquestrador principal que executa todos os 12 stages.
    """
    
    def __init__(self, shadow_corpus_path: str = None):
        self.gf = GFInitialization()
        self.verifier = CitationVerification(shadow_corpus_path)
        self.shadow_acq = ShadowDocumentAcquisition()
        
    def compile(self, article_path: str) -> Dict:
        """Executa o pipeline completo."""
        
        # Stage 1: GF Init
        gf_result = self.gf.initialize()
        
        # Stage 2: Ingestion
        ingestion = ArticleIngestion()
        article = ingestion.ingest_file(article_path)
        if "error" in article:
            return article
        
        # Stage 3: Citation Verification
        citations = ingestion.citations
        verify_result = self.verifier.verify(citations, {})
        
        # Stage 4: Shadow Acquisition
        for cite in citations:
            self.shadow_acq.acquire(cite)
        
        # Stage 5: Claim Extraction
        content = Path(article_path).read_text()
        claim_extractor = ClaimExtraction()
        claims = claim_extractor.extract(content)
        
        # Stage 6: Evidence Extraction  
        evidence_extractor = EvidenceExtraction()
        evidence = evidence_extractor.extract(content, citations)
        
        # Stage 7: GMIF Classification
        for claim in claims:
            claim.gmif_type = GMIFClassification.classify(claim)
        
        # Stage 8: Graph Construction
        graph_builder = GraphConstruction()
        dot_graph = graph_builder.build(claims, evidence)
        
        # Stage 9: Lint
        linter = GraphLint()
        errors = linter.lint(dot_graph, claims, evidence)
        
        # Stage 10: Critical Path
        path_computer = CriticalPathComputation()
        critical_path = path_computer.compute(claims, evidence)
        
        # Stage 11: Fragility
        fragility_analyzer = FragilityAnalysis()
        fragility = fragility_analyzer.analyze(claims, evidence, errors)
        
        # Stage 12: Report
        report_gen = CompilationReportGenerator()
        report = report_gen.generate(
            article["title"],
            claims,
            evidence,
            self.shadow_acq.get_shadows(),
            dot_graph,
            errors,
            critical_path,
            fragility
        )
        
        return asdict(report)


# ============================================================================
# DEMO
# ============================================================================

def demo():
    """Demo do Scientific Compiler."""
    print("=" * 60)
    print("SCIENTIFIC COMPILER - Demo Completo")
    print("=" * 60)
    
    compiler = ScientificCompiler()
    
    # Testar com um ficheiro markdown
    test_file = "/home/rodolfo/src/grilo-falante-skill/docs/gf_scientific_compiler_v_2_spec.md"
    
    if Path(test_file).exists():
        result = compiler.compile(test_file)
        
        print(f"\nArticle: {result['article_title']}")
        print(f"Claims: {len(result['claim_registry'])}")
        print(f"Evidence: {len(result['evidence_registry'])}")
        print(f"Lint errors: {result['lint_report']}")
        print(f"Critical path: {result['critical_path']}")
        print(f"Fragility: {result['fragility_analysis']}")
        
        # Print graph (first 500 chars)
        print(f"\nGMIF Graph (preview):")
        print(result['gmif_graph'][:500])
    else:
        print(f"File not found: {test_file}")


if __name__ == "__main__":
    demo()