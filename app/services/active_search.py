#!/usr/bin/env python3
"""
Active Search - Procura gaps em múltiplas fontes

O Active Search é o segundo passo do "Ir à Escola" loop.
Estratégia de procura (por prioridade):
1. MemPalace local (mais rápido)
2. Docs ambrosio (fontes fidedignas)
3. Web search (fallback)

Autor: Rodolfo
Data: 2026-04-13
"""

import json
import subprocess
import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Resultado de uma procura."""
    query: str
    source: str  # "mempalace", "docs", "web"
    content: str
    relevance: float  # 0-1
    url: Optional[str] = None
    metadata: Optional[Dict] = None


class ActiveSearcher:
    """
    Procura gaps em múltiplas fontes.
    
    Fontes (prioridade):
    1. MemPalace (dados locais)
    2. Docs ambrosio (fontes fidedignas)
    3. Web (fallback)
    """
    
    def __init__(
        self,
        mempalace_path: Optional[str] = None,
        docs_path: Optional[str] = None,
        max_results: int = 3
    ):
        self.mempalace_path = mempalace_path or "/home/rodolfo/.mempalace"
        self.docs_path = docs_path or "/home/rodolfo/Desktop/Grilo_Falante/ambrosio_v2.5.0"
        self.max_results = max_results
        
    def search_mempalace(self, query: str) -> List[SearchResult]:
        """Procura no MemPalace local."""
        results = []
        
        try:
            # Execute mempalace search
            cmd = ["mempalace", "search", query]
            output = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if output.returncode == 0 and output.stdout:
                # Parse output
                lines = output.stdout.split('\n')
                for line in lines[:self.max_results]:
                    if line.strip() and "=" not in line:
                        results.append(SearchResult(
                            query=query,
                            source="mempalace",
                            content=line.strip()[:200],
                            relevance=0.9,
                            metadata={"line": line}
                        ))
                        
        except FileNotFoundError:
            logger.warning("MemPalace not installed")
        except subprocess.TimeoutExpired:
            logger.warning("MemPalace search timeout")
        except Exception as e:
            logger.warning(f"MemPalace search error: {e}")
            
        return results
    
    def search_docs(self, query: str) -> List[SearchResult]:
        """Procura nos docs ambrosio."""
        results = []
        
        if not Path(self.docs_path).exists():
            logger.warning(f"Docs path not found: {self.docs_path}")
            return results
        
        # Simple grep search
        try:
            cmd = [
                "grep", "-r", "-i", "--include=*.md",
                f"-m{self.max_results}",
                query, self.docs_path
            ]
            output = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if output.returncode == 0 and output.stdout:
                lines = output.stdout.split('\n')[:self.max_results]
                for line in lines:
                    if ':' in line:
                        parts = line.split(':', 2)
                        if len(parts) >= 3:
                            file = parts[0]
                            content = parts[2][:150]
                            results.append(SearchResult(
                                query=query,
                                source="ambrosio_docs",
                                content=content,
                                relevance=0.8,
                                metadata={"file": file}
                            ))
                            
        except subprocess.TimeoutExpired:
            logger.warning("Docs search timeout")
        except Exception as e:
            logger.warning(f"Docs search error: {e}")
            
        return results
    
    def search_web(self, query: str) -> List[SearchResult]:
        """Procura na web (fallback)."""
        results = []
        
        # Por agora,return placeholder
        # Em produção, integrar com search API
        logger.info(f"Web search not implemented (would search: {query})")
        
        return results
    
    def search(self, gap_query: str) -> List[SearchResult]:
        """
        Procura principal.
        
        Estrategy:
        1. Try MemPalace
        2. Try docs
        3. Try web
        """
        # Clean query
        query = gap_query.strip()
        if len(query) < 3:
            logger.info(f"Query too short: {query}")
            return []
        
        all_results = []
        
        # 1. MemPalace
        logger.info(f"Searching MemPalace: {query}")
        mp_results = self.search_mempalace(query)
        all_results.extend(mp_results)
        
        # 2. Docs
        if not mp_results:
            logger.info(f"Searching docs: {query}")
            doc_results = self.search_docs(query)
            all_results.extend(doc_results)
        
        # 3. Web (fallback)
        if not all_results:
            logger.info(f"Web fallback: {query}")
            web_results = self.search_web(query)
            all_results.extend(web_results)
        
        if all_results:
            logger.info(f"Found {len(all_results)} results")
        else:
            logger.info(f"No results for: {query}")
        
        return all_results
    
    def search_batch(self, gaps: List[str]) -> Dict[str, List[SearchResult]]:
        """Procura múltiplos gaps de uma vez."""
        results = {}
        
        for gap in gaps:
            results[gap] = self.search(gap)
            
        return results


def demo():
    """Demo do ActiveSearcher."""
    print("=" * 60)
    print("ACTIVE SEARCH - Demo")
    print("=" * 60)
    
    searcher = ActiveSearcher()
    
    test_queries = [
        "Turing",
        "consciência",
        "Grilo Falante",
    ]
    
    for query in test_queries:
        print(f"\n--- Query: {query}")
        results = searcher.search(query)
        
        if results:
            for r in results:
                print(f"  [{r.source}] {r.content[:80]}...")
        else:
            print("  → No results")


if __name__ == "__main__":
    demo()