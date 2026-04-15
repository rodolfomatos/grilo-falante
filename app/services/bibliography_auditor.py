#!/usr/bin/env python3
"""
Bibliography Auditor — Grilo Falante Bibliography Audit Protocol

Implementa o gf_bibliography_audit_prompt.md:

Steps:
1. Reference Candidate Proposal - LLM propõe referências candidatas
2. Human Retrieval - PDF Upload ou Excerpt
3. Shadow Document Creation - Metadata + resumo estruturado
4. Double Feynman Analysis - Lite + Strict
5. Expectation vs Reality - Comparação
6. Claim Coverage Evaluation - FULL/PARTIAL/CONTEXTUAL/MISALIGNED
7. Human Decision - ACCEPT/REJECT
8. Bibliography Integration - .bib + Maps

Autor: Rodolfo
Data: 2026-04-13
"""

import json
import re
import logging
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


# ============================================================================
# DATA CLASSES
# ============================================================================

class ClaimCoverageType(Enum):
    FULL_SUPPORT = "FULL_SUPPORT"
    PARTIAL_SUPPORT = "PARTIAL_SUPPORT"
    CONTEXTUAL_SUPPORT = "CONTEXTUAL_SUPPORT"
    MISALIGNED = "MISALIGNED"


class HumanDecisionType(Enum):
    ACCEPT = "ACCEPT"
    ACCEPT_WITH_LIMITATION = "ACCEPT_WITH_LIMITATION"
    REJECT = "REJECT"


class RetrievalMode(Enum):
    PDF_UPLOAD = "PDF_UPLOAD"
    EXCERPT = "EXCERPT"


@dataclass
class CandidateReference:
    """Step 1: Reference candidate proposed by LLM."""
    id: str
    title: str
    authors: str
    year: int
    relevance: str  # HIGH/MEDIUM/LOW
    domain: str
    doi: Optional[str] = None
    abstract: Optional[str] = None
    verified: bool = False
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "authors": self.authors,
            "year": self.year,
            "relevance": self.relevance,
            "domain": self.domain,
            "doi": self.doi,
            "verified": self.verified
        }


@dataclass
class ShadowDocument:
    """Step 3: Shadow document structure."""
    ref_id: str
    title: str
    authors: str
    year: int
    venue: str
    doi: Optional[str] = None
    
    # Claims extracted
    research_question: str = ""
    main_claims: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    
    # Feynman Analysis
    feynman_lite: str = ""  # Simple summary
    feynman_strict: str = ""   # Precise interpretation
    feynman_not_claim: str = ""  # What paper does NOT claim
    
    # GMIF reliability
    reliability: str = "M3"  # M1-M7
    
    # Metadata
    retrieval_mode: str = "EXCERPT"  # PDF_UPLOAD or EXCERPT
    source_content: str = ""  # The actual content analysed
    
    def to_dict(self) -> Dict:
        return {
            "ref_id": self.ref_id,
            "metadata": {
                "title": self.title,
                "authors": self.authors,
                "year": self.year,
                "venue": self.venue,
                "doi": self.doi
            },
            "content": {
                "research_question": self.research_question,
                "main_claims": self.main_claims,
                "evidence": self.evidence,
                "limitations": self.limitations
            },
            "feynman": {
                "lite": self.feynman_lite,
                "strict": self.feynman_strict,
                "not_claim": self.feynman_not_claim
            },
            "reliability": self.reliability,
            "retrieval_mode": self.retrieval_mode
        }


@dataclass
class ExpectationReality:
    """Step 5: Comparison."""
    expectation: str      # What we thought the source supports
    reality: str       # What the source actually demonstrates
    gap: str          # The difference
    
    def to_dict(self) -> Dict:
        return {
            "expectation": self.expectation,
            "reality": self.reality,
            "gap": self.gap
        }


@dataclass
class ClaimCoverage:
    """Step 6: Claim coverage evaluation."""
    classification: str  # FULL_SUPPORT, PARTIAL_SUPPORT, CONTEXTUAL_SUPPORT, MISALIGNED
    expectation_reality: ExpectationReality
    evidence_quotes: List[str] = field(default_factory=list)
    reasoning: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "classification": self.classification,
            "expectation_reality": self.expectation_reality.to_dict(),
            "evidence_quotes": self.evidence_quotes,
            "reasoning": self.reasoning
        }


@dataclass
class HumanDecision:
    """Step 7: Human decision."""
    decision: str  # ACCEPT, ACCEPT_WITH_LIMITATION, REJECT
    limitation: Optional[str] = None
    rationale: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "decision": self.decision,
            "limitation": self.limitation,
            "rationale": self.rationale,
            "timestamp": self.timestamp
        }


@dataclass
class BibliographyAuditResult:
    """Final result of bibliography audit."""
    candidate: CandidateReference
    shadow_doc: ShadowDocument
    coverage: ClaimCoverage
    decision: HumanDecision
    
    # Claim citation mapping
    claim_id: str = ""
    citation_key: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "candidate": self.candidate.to_dict(),
            "shadow_doc": self.shadow_doc.to_dict(),
            "coverage": self.coverage.to_dict(),
            "decision": self.decision.to_dict(),
            "claim_id": self.claim_id,
            "citation_key": self.citation_key
        }


# ============================================================================
# STEP 1: REFERENCE CANDIDATE PROPOSAL
# ============================================================================

class ReferenceProposer:
    """
    Step 1: Propor referências candidatas relevantes.
    
    O LLM propõe baseado no tema/claim de pesquisa.
    """
    
    def __init__(self):
        self.candidates = []
        self.counter = 0
        
    def generate_candidates(self, topic: str, claim: str = "", max_candidates: int = 5) -> List[CandidateReference]:
        """
        Gera lista de referências candidatas.
        
        Args:
            topic: Tema de pesquisa
            claim: Claim específico (opcional)
            max_candidates: Máximo de candidatos
            
        Returns:
            Lista de CandidateReference
        """
        logger.info(f"Step 1: Proposing candidates for: {topic}")
        
        self.candidates = []
        self.counter = 0
        
        # Common academic databases search patterns (simulated)
        # Em produção, isto chamaria uma API real
        search_patterns = self._generate_search_patterns(topic, claim)
        
        for pattern in search_patterns[:max_candidates]:
            self.counter += 1
            candidate = CandidateReference(
                id=f"CAND-{self.counter:03d}",
                title=pattern["title"],
                authors=pattern["authors"],
                year=pattern["year"],
                relevance=pattern["relevance"],
                domain=pattern["domain"],
                doi=pattern.get("doi"),
                verified=False
            )
            self.candidates.append(candidate)
        
        logger.info(f"Proposed {len(self.candidates)} candidates")
        return self.candidates
    
    def _generate_search_patterns(self, topic: str, claim: str) -> List[Dict]:
        """Generate search patterns (placeholder - em produção usaria API)."""
        # Simulated results - em produção, isto buscaría no Google Scholar/DOI
        patterns = [
            {
                "title": f"Deep Learning for {topic.title()}: A Comprehensive Survey",
                "authors": "Smith, J. and Doe, A.",
                "year": 2023,
                "relevance": "HIGH",
                "domain": "Machine Learning",
                "doi": f"10.1000/ml.{topic.lower().replace(' ','')}"
            },
            {
                "title": f"Neural Approaches to {topic.title()}",
                "authors": "Johnson, B., Garcia, C.",
                "year": 2022,
                "relevance": "HIGH",
                "domain": "Artificial Intelligence",
                "doi": f"10.1000/ai.{topic.lower().replace(' ','')}"
            },
            {
                "title": f"Understanding {topic.title()} through Computational Models",
                "authors": "Williams, D.",
                "year": 2021,
                "relevance": "MEDIUM",
                "domain": "Computational Neuroscience",
                "doi": f"10.1000/cn.{topic.lower().replace(' ','')}"
            }
        ]
        
        if claim:
            # Add claim-specific patterns
            patterns.append({
                "title": f"Evidence for {claim[:50]}...",
                "authors": "Academic Research Team",
                "year": 2024,
                "relevance": "MEDIUM",
                "domain": "General Research",
                "doi": None
            })
        
        return patterns


# ============================================================================
# STEP 2: HUMAN RETRIEVAL HANDLER
# ============================================================================

class HumanRetrievalHandler:
    """
    Step 2: Handle human retrieval.
    
    Two modes:
    - PDF_UPLOAD (preferred)
    - EXCERPT (fallback)
    """
    
    @staticmethod
    def process_pdf_upload(pdf_path: str) -> Dict:
        """
        Processa PDF carregado.
        
        Args:
            pdf_path: Caminho para o PDF
            
        Returns:
            Dict com conteúdo extraído
        """
        logger.info(f"Step 2: Processing PDF: {pdf_path}")
        
        path = Path(pdf_path)
        if not path.exists():
            return {"error": "File not found"}
        
        # Em produção, usaria OCR ou PyPDF2
        # Por agora, retornamos estrutura
        return {
            "mode": "PDF_UPLOAD",
            "filename": path.name,
            "content": "[PDF_CONTENT_WOULD_BE_EXTRACTED_HERE]",
            "pages": 0  # Would be extracted
        }
    
    @staticmethod
    def process_excerpt(citation: str, abstract: str, passages: List[str]) -> Dict:
        """
        Processa excerpt (fallback).
        
        Args:
            citation: Citação verificada
            abstract: Abstract
            passages: Passagens relevantes
            
        Returns:
            Dict com conteúdo
        """
        logger.info("Step 2: Processing excerpt (fallback mode)")
        
        return {
            "mode": "EXCERPT",
            "citation": citation,
            "abstract": abstract,
            "passages": passages,
            "note": "Analysis based on partial source material"
        }
    
    @staticmethod
    def parse_citation(citation_text: str) -> Dict:
        """
        Parses a citation string to extract metadata.
        
        Example: "Smith, J. (2023). Title of paper. Journal Name."
        """
        # Simple parser
        author_match = re.match(r'([A-Z][a-z]+)', citation_text)
        year_match = re.search(r'\((\d{4})\)', citation_text)
        title_match = re.search(r'\.\s+([^.]+)\.', citation_text)
        
        return {
            "authors": author_match.group(1) if author_match else "",
            "year": int(year_match.group(1)) if year_match else 0,
            "title": title_match.group(1).strip() if title_match else ""
        }


# ============================================================================
# STEP 3: SHADOW DOCUMENT CREATION
# ============================================================================

class ShadowDocumentCreator:
    """
    Step 3: Creates shadow document from source.
    """
    
    def create(
        self,
        candidate: CandidateReference,
        source_content: Dict,
        content_type: str = "EXCERPT"
    ) -> ShadowDocument:
        """
        Cria shadow document.
        
        Args:
            candidate: Reference candidate
            source_content: Content from Step 2
            content_type: PDF_UPLOAD or EXCERPT
            
        Returns:
            ShadowDocument
        """
        logger.info(f"Step 3: Creating shadow document for: {candidate.title}")
        
        # Extract metadata
        if content_type == "PDF_UPLOAD":
            content = source_content.get("content", "")
        else:
            content = source_content.get("abstract", "") + "\n" + "\n".join(
                source_content.get("passages", [])
            )
        
        # Extract claims (simplified)
        claims = self._extract_claims(content)
        evidence = self._extract_evidence(content)
        limitations = self._extract_limitations(content)
        
        shadow = ShadowDocument(
            ref_id=candidate.id,
            title=candidate.title,
            authors=candidate.authors,
            year=candidate.year,
            venue="",  # Would be extracted from PDF
            doi=candidate.doi,
            research_question=self._extract_research_question(content),
            main_claims=claims,
            evidence=evidence,
            limitations=limitations,
            retrieval_mode=content_type,
            source_content=content
        )
        
        return shadow
    
    def _extract_research_question(self, content: str) -> str:
        """Extract research question (simplified)."""
        lines = content.split('\n')
        for line in lines:
            if '?' in line and len(line) < 200:
                return line.strip()
        return "Research question not clearly stated"
    
    def _extract_claims(self, content: str) -> List[str]:
        """Extract main claims (simplified pattern matching)."""
        claims = []
        patterns = [
            r'We (?:show|demonstrate|found|argue)',
            r'This (?:paper|study) (?:shows|presents|proposes)',
            r'Results (?:indicate|suggest|show)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                start = max(0, match.start() - 50)
                end = min(len(content), match.end() + 50)
                claims.append(content[start:end].strip())
        
        return claims[:5]  # Limit
    
    def _extract_evidence(self, content: str) -> List[str]:
        """Extract evidence statements."""
        evidence = []
        patterns = [
            r'We (?:collected|observed|measured|found)',
            r'Data (?:shows|indicates|suggests)',
            r'The (?:analysis|results) (?:reveal|show)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                evidence.append(match.group())
        
        return evidence[:3]
    
    def _extract_limitations(self, content: str) -> List[str]:
        """Extract limitations."""
        limitations = []
        
        # Look for limitation patterns
        patterns = [
            r'limitation[s]?\s+(?:include|are)',
            r'However[,.]\s+',
            r'We (?:acknowledge|note|recognize)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                start = max(0, match.start())
                end = min(len(content), match.end() + 100)
                limitations.append(content[start:end].strip())
        
        return limitations[:3]


# ============================================================================
# STEP 4: DOUBLE FEYNMAN ANALYSIS
# ============================================================================

class DoubleFeynmanAnalyzer:
    """
    Step 4: Double Feynman Analysis.
    
    Lite: Simple conceptual explanation
    Strict: Precise interpretation
    """
    
    def analyze(self, shadow: ShadowDocument, target_claim: str = "") -> ShadowDocument:
        """
        Executa análise Feynman dupla.
        
        Args:
            shadow: Shadow document
            target_claim: Claim que queremos validar
            
        Returns:
            ShadowDocument atualizado
        """
        logger.info("Step 4: Double Feynman Analysis")
        
        content = shadow.source_content
        
        # Feynman Lite: simples
        shadow.feynman_lite = self._feynman_lite(content, shadow.main_claims)
        
        # Feynman Strict: preciso
        shadow.feynman_strict = self._feynman_strict(
            content, 
            shadow.main_claims, 
            shadow.evidence
        )
        
        # O que o artigo NÃO klaim
        shadow.feynman_not_claim = self._feynman_not_claim(
            content,
            target_claim
        )
        
        return shadow
    
    def _feynman_lite(self, content: str, claims: List[str]) -> str:
        """Feynman Lite: simples para crianças."""
        if claims:
            # Simplify the first claim
            claim = claims[0][:100]
            return f"O estudo aborda: {claim}. "
        
        return "O estudo aborda um problema de investigação."
    
    def _feynman_strict(self, content: str, claims: List[str], evidence: List[str]) -> str:
        """Feynman Strict: preciso para especialistas."""
        parts = []
        
        if claims:
            parts.append(f"Core claim: {claims[0]}")
        
        if evidence:
            parts.append(f"Evidence: {evidence[0]}")
        
        if not parts:
            parts.append("Unable to extract clear claims from source.")
        
        return " | ".join(parts)
    
    def _feynman_not_claim(self, content: str, target: str) -> str:
        """O que o artigo NÃO klaim."""
        if not target:
            return "No specific claim target provided for comparison."
        
        # Simple check - em produção seria mais sofisticado
        return f"This source does NOT directly claim: '{target[:50]}...'"


# ============================================================================
# STEP 5: EXPECTATION VS REALITY
# ============================================================================

class ExpectationRealityComparator:
    """
    Step 5: Compara expectativa com realidade.
    """
    
    def compare(
        self,
        expectation: str,
        shadow: ShadowDocument
    ) -> ExpectationReality:
        """
        Compara o que esperávamos vs o que o artigo realmente diz.
        
        Args:
            expectation: O que pensávamos que o artigo apoiava
            shadow: Shadow document
            
        Returns:
            ExpectationReality
        """
        logger.info("Step 5: Expectation vs Reality comparison")
        
        reality = shadow.main_claims[0] if shadow.main_claims else "Unable to determine main claim"
        
        # Calcular gap
        gap = self._calculate_gap(expectation, reality)
        
        return ExpectationReality(
            expectation=expectation,
            reality=reality,
            gap=gap
        )
    
    def _calculate_gap(self, expectation: str, reality: str) -> str:
        """Calcula a diferença entre expectativa e realidade."""
        exp_lower = expectation.lower()
        real_lower = reality.lower()
        
        # Check for overlap
        exp_words = set(exp_lower.split())
        real_words = set(real_lower.split())
        
        overlap = exp_words.intersection(real_words)
        
        if len(overlap) > 3:
            return "MINIMAL - Strong alignment"
        elif len(overlap) > 0:
            return "MODERATE - Partial overlap"
        else:
            return "SIGNIFICANT - Misaligned"


# ============================================================================
# STEP 6: CLAIM COVERAGE EVALUATION
# ============================================================================

class ClaimCoverageEvaluator:
    """
    Step 6: Avalia como a fonte apoia a claim.
    
    Classification:
    - FULL_SUPPORT
    - PARTIAL_SUPPORT
    - CONTEXTUAL_SUPPORT
    - MISALIGNED
    """
    
    def evaluate(
        self,
        expectation_reality: ExpectationReality,
        shadow: ShadowDocument,
        target_claim: str
    ) -> ClaimCoverage:
        """
        Avalia cobertura.
        
        Args:
            expectation_reality: Result from Step 5
            shadow: Shadow document
            target_claim: Claim a validar
            
        Returns:
            ClaimCoverage
        """
        logger.info("Step 6: Claim Coverage Evaluation")
        
        gap = expectation_reality.gap
        evidence = shadow.evidence
        
        # Determine classification
        if gap == "SIGNIFICANT - Misaligned":
            classification = ClaimCoverageType.MISALIGNED.value
            reasoning = "Source does not support the claim."
        elif gap == "MODERATE - Partial overlap":
            classification = ClaimCoverageType.PARTIAL_SUPPORT.value
            reasoning = "Source partially supports the claim."
        elif "context" in target_claim.lower():
            classification = ClaimCoverageType.CONTEXTUAL_SUPPORT.value
            reasoning = "Source provides contextual background."
        else:
            classification = ClaimCoverageType.FULL_SUPPORT.value
            reasoning = "Source directly supports the claim."
        
        # Get quotes
        quotes = evidence[:3] if evidence else []
        
        return ClaimCoverage(
            classification=classification,
            expectation_reality=expectation_reality,
            evidence_quotes=quotes,
            reasoning=reasoning
        )


# ============================================================================
# STEP 7: HUMAN DECISION
# ============================================================================

class HumanDecisionRecorder:
    """
    Step 7: Regista decisão humana.
    """
    
    def record(
        self,
        coverage: ClaimCoverage,
        decision: str,
        limitation: Optional[str] = None,
        rationale: str = ""
    ) -> HumanDecision:
        """
        Regista decisão do humano.
        
        Args:
            coverage: Coverage from Step 6
            decision: ACCEPT, ACCEPT_WITH_LIMITATION, REJECT
            limitation: Limitação se aplicável
            rationale: Justificação
            
        Returns:
            HumanDecision
        """
        logger.info(f"Step 7: Human decision: {decision}")
        
        return HumanDecision(
            decision=decision,
            limitation=limitation,
            rationale=rationale or coverage.reasoning
        )
    
    def validate_decision(self, decision: str) -> bool:
        """Valida que decisão é válida."""
        valid = [d.value for d in HumanDecisionType]
        return decision in valid


# ============================================================================
# STEP 8: BIBLIOGRAPHY INTEGRATION
# ============================================================================

class BibliographyIntegrator:
    """
    Step 8: Integra no .bib e gera maps.
    """
    
    def __init__(self, output_dir: str = "graphify-out"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.validation_log_path = self.output_dir / "reference_validation_log.json"
        self.claim_citation_map_path = self.output_dir / "claim_citation_map.json"
        self.bib_path = self.output_dir / "references.bib"
        
        # Load existing or create new
        self.validation_log = self._load_json(self.validation_log_path, [])
        self.claim_citation_map = self._load_json(self.claim_citation_map_path, {})
        self.bib_entries = self._load_bib()
    
    def _load_json(self, path: Path, default: Any) -> Any:
        if path.exists():
            return json.loads(path.read_text())
        return default
    
    def _load_bib(self) -> List[str]:
        """Load existing .bib entries."""
        if self.bib_path.exists():
            return self.bib_path.read_text().split('\n\n')
        return []
    
    def save(
        self,
        result: BibliographyAuditResult,
        claim_id: str = ""
    ) -> Dict:
        """
        Guarda resultado no .bib e atualiza maps.
        
        Args:
            result: BibliographyAuditResult
            claim_id: Claim que está a ser validada
            
        Returns:
            Dict com caminhos dos ficheiros gerados
        """
        logger.info("Step 8: Bibliography integration")
        
        candidate = result.candidate
        shadow = result.shadow_doc
        decision = result.decision
        
        if decision.decision != HumanDecisionType.REJECT.value:
            # Generate BibTeX entry
            bib_entry = self._generate_bibtex(candidate, shadow)
            self.bib_entries.append(bib_entry)
            
            # Generate citation key
            citation_key = self._generate_citation_key(candidate)
            result.citation_key = citation_key
            
            # Update validation log
            self.validation_log.append({
                "timestamp": decision.timestamp,
                "reference": candidate.to_dict(),
                "coverage": result.coverage.to_dict(),
                "decision": decision.to_dict()
            })
            
            # Update claim-citation map
            if claim_id:
                if claim_id not in self.claim_citation_map:
                    self.claim_citation_map[claim_id] = []
                self.claim_citation_map[claim_id].append({
                    "citation_key": citation_key,
                    "coverage": result.coverage.classification,
                    "decision": decision.decision
                })
            
            # Save to files
            self.validation_log_path.write_text(
                json.dumps(self.validation_log, indent=2, ensure_ascii=False)
            )
            self.claim_citation_map_path.write_text(
                json.dumps(self.claim_citation_map, indent=2, ensure_ascii=False)
            )
            self.bib_path.write_text('\n\n'.join(self.bib_entries))
        
        return {
            "bib_file": str(self.bib_path),
            "validation_log": str(self.validation_log_path),
            "claim_citation_map": str(self.claim_citation_map_path)
        }
    
    def _generate_bibtex(self, candidate: CandidateReference, shadow: ShadowDocument) -> str:
        """Gera entrada BibTeX."""
        key = self._generate_citation_key(candidate)
        
        # Handle authors
        authors = candidate.authors.replace(" and ", " and ")
        
        entry = f"@article{{{key},\n"
        entry += f"  author = {{{authors}}},\n"
        entry += f"  title = {{{candidate.title}}},\n"
        entry += f"  year = {{{candidate.year}}},\n"
        
        if shadow.venue:
            entry += f"  journal = {{{shadow.venue}}},\n"
        
        if candidate.doi:
            entry += f"  doi = {{{candidate.doi}}},\n"
        
        entry += "}"
        
        return entry
    
    def _generate_citation_key(self, candidate: CandidateReference) -> str:
        """Generate citation key."""
        first_author = candidate.authors.split(',')[0].split()[0].lower()
        return f"{first_author}{candidate.year}"


# ============================================================================
# MAIN ORCHESTRATOR
# ============================================================================

class BibliographyAuditor:
    """
    Orchestrador principal do Bibliography Audit Protocol.
    
    Executa todos os 8 steps.
    """
    
    def __init__(self, output_dir: str = "graphify-out"):
        self.proposer = ReferenceProposer()
        self.retrieval = HumanRetrievalHandler()
        self.shadow_creator = ShadowDocumentCreator()
        self.feynman = DoubleFeynmanAnalyzer()
        self.comparator = ExpectationRealityComparator()
        self.evaluator = ClaimCoverageEvaluator()
        self.decision_recorder = HumanDecisionRecorder()
        self.integrator = BibliographyIntegrator(output_dir)
    
    def audit(
        self,
        topic: str,
        target_claim: str = "",
        source_content: Dict = None,
        human_decision: str = "ACCEPT"
    ) -> BibliographyAuditResult:
        """
        Executa protocolo completo.
        
        Args:
            topic: Tema de pesquisa
            target_claim: Claim a validar
            source_content: Conteúdo da fonte (Step 2)
            human_decision: Decisão humana (Step 7)
            
        Returns:
            BibliographyAuditResult
        """
        logger.info("=" * 50)
        logger.info("BIBLIOGRAPHY AUDIT PROTOCOL")
        logger.info("=" * 50)
        
        # Step 1: Propose candidates
        candidates = self.proposer.generate_candidates(topic, target_claim)
        candidate = candidates[0]
        
        # Step 2: Source content (provided or placeholder)
        if not source_content:
            source_content = {
                "mode": "EXCERPT",
                "citation": f"{candidate.authors} ({candidate.year}). {candidate.title}.",
                "abstract": "Abstract would be provided here.",
                "passages": ["Key passage 1.", "Key passage 2."]
            }
        
        # Step 3: Create shadow document
        shadow = self.shadow_creator.create(
            candidate, 
            source_content,
            source_content.get("mode", "EXCERPT")
        )
        
        # Step 4: Feynman analysis
        shadow = self.feynman.analyze(shadow, target_claim)
        
        # Step 5: Expectation vs Reality
        expectation = target_claim or f"Reference supports: {topic}"
        expectation_reality = self.comparator.compare(expectation, shadow)
        
        # Step 6: Claim coverage
        coverage = self.evaluator.evaluate(expectation_reality, shadow, target_claim)
        
        # Step 7: Human decision
        decision = self.decision_recorder.record(
            coverage,
            human_decision,
            rationale=f"Human decision based on audit"
        )
        
        # Create result
        result = BibliographyAuditResult(
            candidate=candidate,
            shadow_doc=shadow,
            coverage=coverage,
            decision=decision,
            claim_id=f"CLAIM-{datetime.now().strftime('%y%m%d%H%M')}"
        )
        
        # Step 8: Save to .bib and maps
        self.integrator.save(result, result.claim_id)
        
        return result


# ============================================================================
# DEMO
# ============================================================================

def demo():
    """Demo do Bibliography Auditor."""
    print("=" * 60)
    print("BIBLIOGRAPHY AUDIT PROTOCOL - Demo")
    print("=" * 60)
    
    auditor = BibliographyAuditor()
    
    # Run audit
    result = auditor.audit(
        topic="neural networks consciousness",
        target_claim="consciousness emerges from neural complexity",
        human_decision="ACCEPT"
    )
    
    print(f"\n[RESULT]")
    print(f"Candidate: {result.candidate.title}")
    print(f"Authors: {result.candidate.authors}")
    print(f"Year: {result.candidate.year}")
    print(f"\nCoverage: {result.coverage.classification}")
    print(f"Reasoning: {result.coverage.reasoning}")
    print(f"\nDecision: {result.decision.decision}")
    print(f"\nFeynman Lite: {result.shadow_doc.feynman_lite[:100]}...")
    print(f"\nFeynman Strict: {result.shadow_doc.feynman_strict[:100]}...")
    print(f"\nCitation Key: {result.citation_key}")
    
    print(f"\n[FILES GENERATED]")
    print(f"Bib: {auditor.integrator.bib_path}")
    print(f"Validation Log: {auditor.integrator.validation_log_path}")
    print(f"Claim Map: {auditor.integrator.claim_citation_map_path}")


if __name__ == "__main__":
    demo()