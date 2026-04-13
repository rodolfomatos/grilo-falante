#!/usr/bin/env python3
"""
Feynman Synthesize - Síntese dual (criança + especialista)

O Feynman Synthesize é o terceiro passo do "Ir à Escola" loop.
Gera 2 resumos:
1. Para crianças (7+ anos) - simples, com analogias
2. Para especialistas - técnico, com fontes

Autor: Rodolfo
Data: 2026-04-13
"""

import re
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


@dataclass
class FeynmanSynthesis:
    """Resultado da síntese Feynman."""
    for_child: str       # Resumo para crianças
    for_expert: str     # Resumo para especialistas
    sources_used: List[str]
    gaps_filled: List[str]


class FeynmanSynthesizer:
    """
    Síntese estilo Feynman.
    
   child (< 100 palavras):
    - Sem jargão técnico
    - Com analogias do dia-a-dia
    - Linguagem simples
    
    expert (< 500 palavras):
    - Precisão técnica
    - Fontes referenciadas
    - Com nuance
    """
    
    # Palavras simples para kids
    SIMPLE_WORDS = {
        "consciência": "consciência é como uma lanterna",
        "IA": "computador que pensa",
        "memória": "uma gaveta na mente",
        "aprendizagem": "aprender é como grow",
        "algoritmo": "receita de bolo",
        "neurónio": "pequena célula",
        "sinapse": "ponte entre células",
    }
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        
    def simplify_for_child(self, content: str, max_words: int = 50) -> str:
        """
        Versão simplificada para crianças.
        
        Estratégia:
        - Substituir termos técnicos por analogias
        - Frases curtas
        - Linguagem do dia-a-dia
        """
        text = content.strip()
        
        # Substituir termos técnicos
        for term, simple in self.SIMPLE_WORDS.items():
            text = re.sub(
                rf'\b{term}s?\b',
                simple,
                text,
                flags=re.IGNORECASE
            )
        
        # Limpar pontuação excessiva
        text = re.sub(r'[^\w\s,.\-áéíóúàèìòùãẽĩõũç?!]', '', text)
        
        # Split em palavras
        words = text.split()
        
        if len(words) <= max_words:
            return text
        
        # Truncar com ellipsis
        return ' '.join(words[:max_words]) + '...'
    
    def make_expert(self, content: str, sources: List[str], max_words: int = 200) -> str:
        """
        Versão para especialistas.
        
        Estratégia:
        - Manter precisão técnica
        - Adicionar nuances
        - Referenciar fontes
        """
        text = content.strip()
        
        # Adicionar fontes
        if sources:
            source_refs = "\n**Fontes:** " + ", ".join(sources[:3])
            if len(text) + len(source_refs) < max_words * 5:
                text += source_refs
        
        # Split em palavras
        words = text.split()
        
        if len(words) <= max_words:
            return text
        
        # Truncar
        return ' '.join(words[:max_words]) + '...'
    
    def synthesize(
        self,
        gap: str,
        search_results: List[Dict]
    ) -> FeynmanSynthesis:
        """
        Síntese principal.
        
        Args:
            gap: O gap que we're filling
            search_results: Resultados da procura
            
        Returns:
            FeynmanSynthesis object
        """
        logger.info(f"Synthesizing for: {gap}")
        
        # Collect content from all sources
        all_content = []
        sources = []
        
        for result in search_results:
            content = result.get("content", "")
            if content:
                all_content.append(content)
                sources.append(result.get("source", "unknown"))
        
        combined = "\n\n".join(all_content)
        
        if not combined:
            return FeynmanSynthesis(
                for_child=f"Não encontrei informação sobre {gap}.",
                for_expert=f"No information found for query: {gap}",
                sources_used=[],
                gaps_filled=[gap]
            )
        
        # Generate both versions
        child_version = self.simplify_for_child(combined)
        expert_version = self.make_expert(combined, sources)
        
        return FeynmanSynthesis(
            for_child=child_version,
            for_expert=expert_version,
            sources_used=sources,
            gaps_filled=[gap]
        )
    
    def synthesize_batch(
        self,
        gaps: List[str],
        all_results: Dict[str, List[Dict]]
    ) -> Dict[str, FeynmanSynthesis]:
        """Sintetiza múltiplos gaps."""
        results = {}
        
        for gap in gaps:
            search_results = all_results.get(gap, [])
            results[gap] = self.synthesize(gap, search_results)
            
        return results


def demo():
    """Demo do FeynmanSynthesizer."""
    print("=" * 60)
    print("FEYNMAN SYNTHESIZE - Demo")
    print("=" * 60)
    
    synth = FeynmanSynthesizer()
    
    test_contents = [
        {
            "gap": "Alan Turing",
            "results": [
                {
                    "content": "Alan Mathison Turing (1912-1954) was a British mathematician and computer scientist. He is considered the father of theoretical computer science and artificial intelligence.",
                    "source": "wikipedia"
                },
                {
                    "content": "Turing developed the Turing machine concept, a fundamental model for understanding computation.",
                    "source": "academic"
                }
            ]
        },
        {
            "gap": "consciência",
            "results": [
                {
                    "content": "Consciousness is the quality or state of being aware of something. In philosophy, it refers to subjective experience.",
                    "source": "philosophy"
                }
            ]
        }
    ]
    
    for test in test_contents:
        print(f"\n--- Gap: {test['gap']}")
        synthesis = synth.synthesize(test["gap"], test["results"])
        
        print(f"  Para crianças:")
        print(f"    {synthesis.for_child}")
        
        print(f"  Para especialistas:")
        print(f"    {synthesis.for_expert[:100]}...")


if __name__ == "__main__":
    demo()