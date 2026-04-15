#!/usr/bin/env python3
"""
Ir à Escola Orchestrator - Junta tudo

Este móduloorchestra todo o "Ir à Escola" loop:
1. Gap Detection → O que não sei?
2. Active Search → Onde procurar?
3. Feynman Synthesize → Como explicar?
4. Why Loop → Porquê?
5. Persist → Guardar no MemPalace

Autor: Rodolfo
Data: 2026-04-13
"""

import json
import logging
import sys
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Importar serviços locais
from app.services.gap_detector import GapDetector, Gap
from app.services.active_search import ActiveSearcher, SearchResult
from app.services.feynman_synthesize import FeynmanSynthesizer, FeynmanSynthesis
from app.services.why_loop import WhyLoop

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


@dataclass
class SchulReiseResult:
    """Resultado completo do 'Ir à Escola'."""
    conversation_id: str
    original_message: str
    timestamp: str
    gaps_detected: List[str]
    sources_used: List[Dict]
    feynman_child: str
    feynman_expert: str
    why_questions: List[Dict]
    gf_id: str
    status: str


class IrAEscolaOrchestrator:
    """
    Orquestrador principal do "Ir à Escola".
    
    Usage:
        orchestrator = IrAEscolaOrchestrator()
        result = orchestrator.run("mensagem do utilizador")
    """
    
    def __init__(self):
        # Inicializar serviços
        self.gap_detector = GapDetector()
        self.searcher = ActiveSearcher()
        self.synthesizer = FeynmanSynthesizer()
        self.why_loop = WhyLoop()
        
    def generate_gf_id(self, gap: str) -> str:
        """Gera GF-ID único."""
        date = datetime.now().strftime("%y%m%d")
        short_hash = gap[:6] if gap else "empty"
        return f"GF-{date}-ESCOLA-{short_hash}"
    
    def store_in_mempalace(self, result: SchulReiseResult) -> bool:
        """Guarda resultado no MemPalace."""
        try:
            # Por agora,guardar JSON
            output_dir = "/home/rodolfo/src/grilo-falante-skill/graphify-out"
            import os
            os.makedirs(output_dir, exist_ok=True)
            
            output_file = f"{output_dir}/ir_a_escola_{result.conversation_id}.json"
            
            with open(output_file, 'w') as f:
                json.dump(asdict(result), f, ensure_ascii=False, indent=2)
                
            logger.info(f"Saved to: {output_file}")
            return True
            
        except Exception as e:
            logger.warning(f"Could not store: {e}")
            return False
    
    def run(self, message: str, max_gaps: int = 5) -> SchulReiseResult:
        """
        Executa o loop completo.
        
        Args:
            message: Mensagem do utilizador
            
        Returns:
            SchulReiseResult object
        """
        logger.info("=" * 40)
        logger.info("IR À ESCOLA - Starting")
        logger.info("=" * 40)
        
        conversation_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()
        
        # 1. Detect gaps
        logger.info("Step 1: Detecting gaps...")
        gaps = self.gap_detector.detect(message, max_gaps=max_gaps)
        gap_texts = [g.text for g in gaps]
        
        if not gap_texts:
            logger.info("No gaps detected - answering normally")
            return SchulReiseResult(
                conversation_id=conversation_id,
                original_message=message,
                timestamp=timestamp,
                gaps_detected=[],
                sources_used=[],
                feynman_child="Não tenho gaps para preencher.",
                feynman_expert="No gaps detected.",
                why_questions=[],
                gf_id=self.generate_gf_id(message),
                status="no_gaps"
            )
        
        logger.info(f"Found {len(gap_texts)} gaps: {gap_texts}")
        
        # 2. Search
        logger.info("Step 2: Searching...")
        all_results = {}
        sources_used = []
        
        for gap in gap_texts:
            results = self.searcher.search(gap)
            all_results[gap] = [
                {"content": r.content, "source": r.source}
                for r in results
            ]
            sources_used.extend(all_results[gap])
        
        # 3. Synthesize
        logger.info("Step 3: Synthesizing...")
        # Combine results para síntese
        combined_results = []
        for gap in gap_texts:
            combined_results.extend(all_results.get(gap, []))
        
        synthesis = self.synthesizer.synthesize(
            gap_texts[0] if gap_texts else message,
            combined_results
        )
        
        # 4. Why loop
        logger.info("Step 4: Generating why questions...")
        why_result = self.why_loop.run_loop(synthesis, gap_texts[0] if gap_texts else message)
        
        # 5. Create result
        gf_id = self.generate_gf_id(gap_texts[0] if gap_texts else message)
        
        result = SchulReiseResult(
            conversation_id=conversation_id,
            original_message=message,
            timestamp=timestamp,
            gaps_detected=gap_texts,
            sources_used=sources_used,
            feynman_child=synthesis.for_child,
            feynman_expert=synthesis.for_expert,
            why_questions=why_result.get("questions", []),
            gf_id=gf_id,
            status="complete"
        )
        
        # 6. Store
        logger.info("Step 5: Storing...")
        self.store_in_mempalace(result)
        
        logger.info("=" * 40)
        logger.info("IR À ESCOLA - Complete")
        logger.info("=" * 40)
        
        return result
    
    def run_simple(self, message: str) -> Dict:
        """Versão simples que devolve dict."""
        result = self.run(message)
        return asdict(result)


def demo():
    """Demo do IrAEscolaOrchestrator."""
    print("=" * 60)
    print("IR À ESCOLA - Full Demo")
    print("=" * 60)
    
    orchestrator = IrAEscolaOrchestrator()
    
    test_messages = [
        # Com factos conhecidos
        "Alan Turing nasceu em 1912 na Índia.",
        
        # Com conceitos
        "O que é consciência quântica?",
        
        # Sem factos
        "Olá, como estás?",
    ]
    
    for msg in test_messages:
        print(f"\n{'='*60}")
        print(f"MENSAGEM: {msg}")
        print(f"{'='*60}")
        
        result = orchestrator.run(msg)
        
        print(f"\nGaps: {result.gaps_detected}")
        print(f"\nPara crianças:")
        print(f"  {result.feynman_child}")
        print(f"\nPara especialistas:")
        print(f"  {result.feynman_expert[:100]}...")
        print(f"\nGF-ID: {result.gf_id}")
        print(f"Status: {result.status}")


if __name__ == "__main__":
    demo()