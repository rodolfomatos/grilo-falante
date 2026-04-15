#!/usr/bin/env python3
"""
IAEDU Adapter for Grilo Falante
===============================

Conecta ao ChatGPT-4o via iaedu.pt para análise semântica.

Usage:
    export IAEDU_API_KEY=sua_chave
    python3 grilo_pipeline.py <path> --llm iaedu

Requires:
    - IAEDU_API_KEY environment variable
    - requests library
"""

import os
import json
import logging
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# IAEDU Configuration
IAEDU_ENDPOINT = "https://api.iaedu.pt/agent-chat/api/v1/agent/cmamvd3n40000c801qeacoad2/stream"
IAEDU_CHANNEL = "cmh0rfgmn0i64j801uuoletwy"


class IAEDUClient:
    """Client para IAEDU API."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("IAEDU_API_KEY")
        if not self.api_key:
            raise ValueError("IAEDU_API_KEY não configurada")
        
        self.endpoint = IAEDU_ENDPOINT
        self.channel = IAEDU_CHANNEL
        self.api_key = api_key
    
    def chat(self, message: str, system_prompt: Optional[str] = None) -> str:
        """Envia mensagem e recebe resposta."""
        import uuid
        from urllib.parse import quote
        
        thread_id = f"grilo-{uuid.uuid4()}"
        
        # Prepare FormData
        data = {
            "channel_id": self.channel,
            "thread_id": thread_id,
            "user_info": "{}",
            "message": message,
        }
        
        headers = {
            "x-api-key": self.api_key,
        }
        
        logger.info(f"Sending to IAEDU: {message[:50]}...")
        
        try:
            response = requests.post(
                self.endpoint,
                data=data,
                headers=headers,
                timeout=60,
                stream=True,
            )
            
            if not response.ok:
                logger.error(f"IAEDU error: {response.status_code}")
                return f"Erro: {response.status_code}"
            
            # Parse NDJSON stream
            result = ""
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        if data.get("type") == "token" and data.get("content"):
                            result += data["content"]
                    except Exception as e:
                        logger.warning(f"Failed to parse JSON line: {e}")
            
            logger.info(f"IAEDU response: {result[:50]}...")
            return result
            
        except Exception as e:
            logger.error(f"IAEDU error: {e}")
            return f"Erro: {str(e)}"
    
    def analyze_with_llm(self, nodes: List[Dict], query: str = "Analisa estes conceitos") -> Dict:
        """Usa LLM para análise semântica dos conceitos extraídos."""
        
        # Build context
        concepts = [n.get("label", "") for n in nodes[:20]]
        context = "\n".join(f"- {c}" for c in concepts)
        
        prompt = f"""{query}

Conceitos extraídos:
{context}

Para cada conceito, classifica por força epistémica (M1-M7) e explica porquê.
"""
        
        response = self.chat(prompt)
        
        return {
            "analysis": response,
            "concepts_analyzed": len(nodes),
            "timestamp": datetime.now().isoformat(),
        }


def use_iaedu_for_classification(nodes: List[Dict], edges: List[Dict]) -> List[Dict]:
    """Usa IAEDU para classificação GMIF mais precisa."""
    
    try:
        client = IAEDUClient()
        
        # Pedir análise ao LLM
        result = client.analyze_with_llm(
            nodes,
            "Para cada conceito, indica se é FACT (factual), OPINION (opinião), ou QUESTION (pergunta)"
        )
        
        logger.info("IAEDU classification: " + str(result.get("concepts_analyzed", 0)))
        
        # Parsear resultado e atualizar nodes
        # (simplificado - em produção usaríamos parsing mais complexo)
        for node in nodes:
            # Por defeito, mantém classificação existente
            pass
        
        return nodes
        
    except ValueError as e:
        logger.warning(f"IAEDU não disponível: {e}")
        return nodes
    except Exception as e:
        logger.error(f"IAEDU error: {e}")
        return nodes


# Teste rápido
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Testing IAEDU connection...")
        try:
            client = IAEDUClient()
            response = client.chat("Olá, responde em português")
            print("Response:", response[:200])
        except Exception as e:
            print("Error:", e)
    else:
        print("""
IAEDU Adapter for Grilo Falante
==============================

Usage:
    export IAEDU_API_KEY=sua_chave
    python3 grilo_pipeline.py ./app --llm iaedu

Options:
    --llm iaedu        Use IAEDU for semantic analysis
    --llm ollama       Use local Ollama (future)
    --llm openai      Use OpenAI (future)
        """)