#!/usr/bin/env python3
"""
Gap Detector - Detecta factos que não sabe numa mensagem

O Gap Detector é o primeiro passo do "Ir à Escola" loop.
Funciona assim:
1. Recebe uma mensagem
2. Extrai claims (afirmações factuais)
3. Para cada claim, verifica se já sabe no MemPalace
4. Devolve lista de "gaps" (coisas que não sabe)

Autor: Rodolfo
Data: 2026-04-13
"""

import re
import logging
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


@dataclass
class Gap:
    """Um "gap" = coisa que não sei."""
    text: str
    type: str  # "fact", "person", "date", "place", "concept", "claim"
    confidence: float  # 0-1, how likely it's a factual claim
    context: str  # surrounding text
    source_indicators: List[str]  # words that suggest factual content


class GapDetector:
    """
    Detecta gaps (coisas que não sei) numa mensagem.
    
    Estratégia:
    - Patterns para factos (datas, nomes, números)
    - Check no MemPalace
    - Return gaps não encontrados
    """
    
    # Patterns que indicam claims factuais
    FACT_PATTERNS = [
        # Datas
        (r'\b\d{4}\b', 'date'),
        (r'\b\d{1,2}\s+de\s+\w+(?:\s+de\s+\d{4})?\b', 'date'),
        (r'\bem\s+\d{4}\b', 'date'),
        
        # Nomes próprios (capitalizados)
        (r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', 'person'),
        
        # Organizações
        (r'\b(?:Universidad|Faculdade|Instituto|Museu|Clínica|Hospital)\s+[A-Z]', 'organization'),
        
        # Lugares com preposição
        (r'\b(?:em|no|na|no|na)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', 'place'),
        
        # Números específicos
        (r'\b\d+(?:\.\d+)?\s*(?:%|por cento|anos|milhões?|bilhões?)?\b', 'number'),
        
        # Termos técnicos sem pontos de interrogação (não é pergunta)
        (r'\bé\b.*\b(?:teoria|hipótese|fenómeno|princípio|lei|modelo)\b', 'concept'),
        
        # Afirmações com verbos de estado
        (r'\b(?:foi|é|foi|existe|foi\s+creado|fundou)\b\s+\w+', 'claim'),
    ]
    
    # Ignore patterns (não são factual claims)
    IGNORE_PATTERNS = [
        r'^\s*Quem\s',  # perguntas que começam com Quem
        r'^\s*O\s+que\s',
        r'^\s*Como\s',
        r'^\s*Por\s+qu',
        r'^\s*Qual\s',
        r'^\s*Quando\s',
        r'^\s*Onde\s',
    ]
    
    def __init__(self, mempalace_client=None):
        self.mempalace_client = mempalace_client
        self.known_facts: Set[str] = set()
        
    def load_known_facts(self):
        """Carrega factos conhecidos do MemPalace."""
        # Por agora,load básico
        # TODO: Integrar com MemPalace real
        try:
            result = self.mempalace_client.search("*") if self.mempalace_client else None
            if result:
                # Parse e guarda factos
                logger.info("Loaded known facts from MemPalace")
        except Exception as e:
            logger.warning(f"Could not load known facts: {e}")
    
    def extract_claims(self, text: str) -> List[Dict]:
        """
        Extrai claims factuais de um texto.
        
        Returns:
            Lista de dicts com 'text', 'type', 'confidence'
        """
        claims = []
        
        # Skip se é pergunta
        for ignore in self.IGNORE_PATTERNS:
            if re.search(ignore, text):
                logger.info(f"Skipping (question): {text[:50]}")
                return []
        
        # Extract por cada pattern
        for pattern, claim_type in self.FACT_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                start = max(0, match.start() - 30)
                end = min(len(text), match.end() + 30)
                context = text[start:end]
                
                # Skip se muito curto ou muito longo
                if len(match.group()) < 2 or len(match.group()) > 100:
                    continue
                    
                claims.append({
                    "text": match.group(),
                    "type": claim_type,
                    "confidence": 0.8,  # default
                    "context": f"...{context}...",
                    "position": match.start()
                })
        
        # Deduplicate
        seen = set()
        unique = []
        for c in claims:
            if c["text"] not in seen:
                seen.add(c["text"])
                unique.append(c)
        
        # Sort por posição
        unique.sort(key=lambda x: x["position"])
        
        return unique
    
    def is_known(self, claim: str) -> bool:
        """Verifica se fact já é conhecido."""
        # Normalize
        normalized = claim.lower().strip()
        
        if normalized in self.known_facts:
            return True
        
        # Check MemPalace
        if self.mempalace_client:
            try:
                result = self.mempalace_client.search(claim)
                if result and result.get("matches"):
                    return True
            except:
                pass
        
        return False
    
    def detect(self, text: str, max_gaps: int = 5) -> List[Gap]:
        """
        DETETOR PRINCIPAL.
        
        Args:
            text: Mensagem do utilizador
            max_gaps: Máximo de gaps a devolver
            
        Returns:
            Lista de Gap objects
        """
        # Extract claims
        claims = self.extract_claims(text)
        
        if not claims:
            logger.info("No factual claims detected")
            return []
        
        # Check cada claim
        gaps = []
        for claim_data in claims:
            claim_text = claim_data["text"]
            
            # Skip se já conhecido
            if self.is_known(claim_text):
                logger.info(f"Known: {claim_text}")
                continue
            
            # Skip se muito genérico
            if len(claim_text) < 3:
                continue
            
            # Skip se muito comum
            common_words = {"não", "sim", "mais", "menos", "muito", "pouco", "todo"}
            if claim_text.lower() in common_words:
                continue
            
            # Create Gap
            gap = Gap(
                text=claim_text,
                type=claim_data["type"],
                confidence=claim_data["confidence"],
                context=claim_data["context"],
                source_indicators=[]
            )
            gaps.append(gap)
            
            if len(gaps) >= max_gaps:
                break
        
        logger.info(f"Detected {len(gaps)} gaps")
        return gaps
    
    def detect_simple(self, text: str) -> List[str]:
        """
        Versão simples que devolve só texto.
        Útil para debugging.
        """
        gaps = self.detect(text)
        return [g.text for g in gaps]


def demo():
    """Demo do GapDetector."""
    print("=" * 60)
    print("GAP DETECTOR - Demo")
    print("=" * 60)
    
    detector = GapDetector()
    
    test_messages = [
        # Claims factuais
        "Alan Turing nasceu em 1912 e criou a máquina de Turing.",
        "A Segunda Guerra Mundial começou em 1939.",
        "O museu do Louvre está em Paris.",
        "A FEUP é a Faculdade de Engenharia da Universidade do Porto.",
        
        # Perguntas (não deve extrair)
        "Quem foi Alan Turing?",
        "O que é consciência?",
        "Pode me dizer quem foi Turing?",
        
        #uzzy (não deve extrair)
        "Acho que talvez seja verdade.",
        "Não sei se isto está certo.",
    ]
    
    for msg in test_messages:
        print(f"\n--- Mensagem: {msg}")
        gaps = detector.detect(msg)
        if gaps:
            for g in gaps:
                print(f"  → GAP [{g.type}]: {g.text}")
        else:
            print("  → Nenhum gap")


if __name__ == "__main__":
    demo()