#!/usr/bin/env python3
"""
AI-to-AI Conversation Test - Two IAs talking to each other

This script creates a conversation between two AI agents:
- Agent A: Has Grilo Falante regime (context, islands, claims, GMIF)
- Agent B: Regular AI without regime

The goal is to see how context understanding evolves and how
claims are extracted, classified, and stored.

Usage:
    python3 test_ai_to_ai.py
    python3 test_ai_to_ai.py --topic "mudanças climáticas"
    python3 test_ai_to_ai.py --rounds 5
"""

import asyncio
import argparse
import json
import sys
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from grilo_falante.platform.config import get_llm_config, LLMClient


class AgentType(str, Enum):
    GRILO_FALANTE = "grilo_falante"
    REGULAR = "regular"


@dataclass
class Message:
    """A message in the conversation."""
    agent: AgentType
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    gmif_level: Optional[str] = None
    claims_extracted: List[str] = field(default_factory=list)
    gaps_identified: List[str] = field(default_factory=list)


@dataclass
class Claim:
    """An extracted claim from a message."""
    id: str
    text: str
    gmif_level: str
    confidence: float
    session_id: str
    validated: bool = False


class ClaimExtractor:
    """Extracts claims from text using simple heuristics."""

    GMIF_KEYWORDS = {
        "M1": ["estudos confirmam", "evidência demonstra", "dados oficiais", " múltiplas fontes"],
        "M2": ["depende de", "válido quando", "sob condição", " pressesuposto que"],
        "M3": ["pode ser", "talvez", "possivelmente", "parece que"],
        "M4": ["contradiz", "contradição", "inconsistente", "duvidoso"],
        "M5": ["segundo", "de acordo com", "fonte indica", "relatório diz"],
        "M6": ["portanto", "consequentemente", "logicamente", "deduz-se que"],
    }

    @classmethod
    def extract(cls, text: str) -> List[Dict[str, Any]]:
        """Extract claims from text."""
        import re

        claims = []

        patterns = [
            r'([A-Z][a-z]+(?:[a-z]+)*\s+(?:é|foi|são|foram|será|deve|pode)\s+[^\.!?]+[^\.!?])',
            r'(?:O|A)\s+([a-z]+(?:\s+[a-z]+)*\s+(?:é|foi|são|foram)\s+[^\.!?]+)',
            r'([^\.!?]*(?:confirmado|demonstrado|provado|evidenciado)[^\.!?]+)',
        ]

        found_texts = set()
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match) > 20 and len(match) < 400 and match not in found_texts:
                    found_texts.add(match)
                    claims.append(match.strip())

        if not claims:
            sentences = text.replace('?', '.').replace('!', '.').split('.')
            for sent in sentences:
                sent = sent.strip()
                if len(sent) > 30 and len(sent) < 300:
                    claims.append(sent)

        results = []
        for i, claim_text in enumerate(claims[:5]):
            gmif, confidence = cls._classify_claim(claim_text)
            results.append({
                "text": claim_text,
                "gmif_level": gmif,
                "confidence": confidence,
            })

        return results

    @classmethod
    def _classify_claim(cls, text: str) -> tuple[str, float]:
        """Classify a claim using GMIF."""
        text_lower = text.lower()

        scores = {}
        for level, keywords in cls.GMIF_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw.lower() in text_lower)
            scores[level] = score

        if max(scores.values()) == 0:
            return "M3", 0.5

        best_level = max(scores, key=scores.get)
        confidence = min(0.9, 0.3 + scores[best_level] * 0.15)

        return best_level, confidence


class GapDetector:
    """Detects gaps (questions/uncertainties) in text."""

    @classmethod
    def detect(cls, text: str) -> List[str]:
        """Detect gaps (questions and uncertainties)."""
        import re

        gaps = []

        questions = re.findall(r'([^\?]*\?)', text)
        for q in questions[:3]:
            q = q.strip()
            if len(q) > 10:
                gaps.append(q)

        uncertainty_patterns = [
            r'não sei',
            r'não tenho certeza',
            r'preciso de verificar',
            r'haveria necessidade de',
            r'como exatamente',
            r'o que acontece se',
            r'porque será que',
        ]

        for pattern in uncertainty_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                match = re.search(rf'([^\.!?]*{pattern}[^\.!?]+)', text, re.IGNORECASE)
                if match:
                    gap = match.group(0).strip()
                    if len(gap) > 10:
                        gaps.append(gap)

        return list(set(gaps))[:5]


class AIAgent:
    """Base AI agent."""

    def __init__(self, name: str, agent_type: AgentType, llm_client: Optional[LLMClient] = None):
        self.name = name
        self.agent_type = agent_type
        self.llm_client = llm_client or LLMClient()
        self.conversation_history: List[Message] = []
        self.claims: List[Claim] = []
        self.context: Dict[str, Any] = {}

    async def think(self, prompt: str) -> str:
        """Generate a response using the LLM."""
        try:
            system_prompt = self._get_system_prompt()
            response = await self.llm_client.generate(prompt, system_prompt=system_prompt)
            return response
        except Exception as e:
            return self._mock_response(prompt)

    def _mock_response(self, prompt: str) -> str:
        """Generate a mock response when LLM is not available."""
        if self.agent_type == AgentType.GRILO_FALANTE:
            return f"[MOCK - Grilo Falante] Regarding your question about the topic: This is a significant area of study with multiple perspectives. What specific aspect would you like to explore? I can help identify claims and classify them by epistemic confidence."
        else:
            return f"[MOCK - Regular AI] Thank you for your message. This is an interesting topic that deserves careful consideration. Could you elaborate on what aspects you're most interested in understanding?"

    def _get_system_prompt(self) -> Optional[str]:
        """Get system prompt based on agent type."""
        if self.agent_type == AgentType.REGULAR:
            return None

        return """You are Grilo Falante, an AI with epistemic governance.
You maintain context through islands of knowledge.
You extract claims and classify them by confidence (GMIF M1-M8).
You identify gaps in knowledge and ask clarifying questions.
You are rigorous but accessible in your explanations."""

    def process_response(self, response: str) -> Dict[str, Any]:
        """Process a response to extract claims and gaps."""
        claims = ClaimExtractor.extract(response)
        gaps = GapDetector.detect(response)

        return {
            "claims": claims,
            "gaps": gaps,
        }


class GriloFalanteAgent(AIAgent):
    """Agent with Grilo Falante regime."""

    def __init__(self, name: str, llm_client: Optional[LLMClient] = None):
        super().__init__(name, AgentType.GRILO_FALANTE, llm_client)
        self.islands: List[Dict[str, Any]] = []
        self.saliência_threshold = 0.5

    def _get_system_prompt(self) -> str:
        return """You are Grilo Falante, an AI with epistemic governance.

Your principles:
1. Every claim must be classified by epistemic confidence (GMIF M1-M8)
2. M1 = Primary evidence (multiple sources, high confidence)
3. M4 = Doubtful (contradictions or weak evidence)
4. When uncertain, identify the GAP and suggest how to fill it
5. Maintain islands of consolidated knowledge
6. Be rigorous but accessible

When you make a claim, prefix it with [M1], [M2], etc.
When you don't know something, say "GAP: ..." and explain what's needed."""

    def create_island(self, topic: str) -> Dict[str, Any]:
        """Create a new island of knowledge."""
        island = {
            "id": f"ILHA-{len(self.islands)+1:03d}",
            "topic": topic,
            "claims": [],
            "gaps": [],
            "activation_score": 0.5,
            "state": "EMBRIONARIA",
        }
        self.islands.append(island)
        return island

    def add_claim_to_island(self, island_id: str, claim: Dict[str, Any]) -> bool:
        """Add a claim to an island."""
        for island in self.islands:
            if island["id"] == island_id:
                island["claims"].append(claim)
                return True
        return False


class RegularAgent(AIAgent):
    """Regular AI agent without Grilo regime."""

    def __init__(self, name: str, llm_client: Optional[LLMClient] = None):
        super().__init__(name, AgentType.REGULAR, llm_client)


class ConversationSimulator:
    """Simulates a conversation between two AI agents."""

    def __init__(
        self,
        agent_a: AIAgent,
        agent_b: AIAgent,
        topic: str,
        rounds: int = 3,
    ):
        self.agent_a = agent_a
        self.agent_b = agent_b
        self.topic = topic
        self.rounds = rounds
        self.conversation: List[Message] = []
        self.all_claims: List[Dict[str, Any]] = []

    async def run(self) -> Dict[str, Any]:
        """Run the full conversation."""
        print("=" * 70)
        print(f"AI-TO-AI CONVERSATION: {self.agent_a.name} vs {self.agent_b.name}")
        print(f"TOPIC: {self.topic}")
        print("=" * 70)
        print()

        opener_prompt = f"""Start a conversation about: {self.topic}

You are {self.agent_a.name}. Introduce the topic briefly and share 2-3 key points or questions.

Be natural and conversational."""

        current_a = opener_prompt
        current_b = None

        for round_num in range(self.rounds):
            print(f"\n{'─' * 70}")
            print(f"ROUND {round_num + 1}")
            print(f"{'─' * 70}")

            print(f"\n📤 {self.agent_a.name} → {self.agent_b.name}:")
            response_a = await self.agent_a.think(current_a)
            print(f"   {response_a[:300]}...")

            processed_a = self.agent_a.process_response(response_a)
            msg_a = Message(
                agent=self.agent_a.agent_type,
                content=response_a,
                claims_extracted=[c["text"] for c in processed_a["claims"]],
                gaps_identified=processed_a["gaps"],
            )
            self.conversation.append(msg_a)
            self.all_claims.extend(processed_a["claims"])

            if processed_a["claims"]:
                print(f"   📋 Claims extracted: {len(processed_a['claims'])}")
                for c in processed_a["claims"][:2]:
                    print(f"      [{c['gmif_level']}] {c['text'][:60]}...")

            if processed_a["gaps"]:
                print(f"   ❓ Gaps identified: {len(processed_a['gaps'])}")

            print(f"\n📤 {self.agent_b.name} → {self.agent_a.name}:")
            response_b = await self.agent_b.think(
                f"Previous message: {response_a}\n\nYour turn to respond about {self.topic}. Be conversational and ask follow-up questions."
            )
            print(f"   {response_b[:300]}...")

            processed_b = self.agent_b.process_response(response_b)
            msg_b = Message(
                agent=self.agent_b.agent_type,
                content=response_b,
                claims_extracted=[c["text"] for c in processed_b["claims"]],
                gaps_identified=processed_b["gaps"],
            )
            self.conversation.append(msg_b)
            self.all_claims.extend(processed_b["claims"])

            if processed_b["claims"]:
                print(f"   📋 Claims extracted: {len(processed_b['claims'])}")

            current_a = f"Continue the conversation about {self.topic}. The other agent said: {response_b[:500]}"
            current_b = response_b

        return self._generate_report()

    def _generate_report(self) -> Dict[str, Any]:
        """Generate a final report of the conversation."""
        print("\n" + "=" * 70)
        print("CONVERSATION REPORT")
        print("=" * 70)

        grilo_claims = [c for c in self.all_claims if c.get("gmif_level")]
        regular_claims = [c for c in self.all_claims if not c.get("gmif_level")]

        gmif_dist = {}
        for c in grilo_claims:
            level = c.get("gmif_level", "unknown")
            gmif_dist[level] = gmif_dist.get(level, 0) + 1

        print(f"\n📊 STATISTICS:")
        print(f"   Total messages: {len(self.conversation)}")
        print(f"   Total claims extracted: {len(self.all_claims)}")
        print(f"   Claims with GMIF: {len(grilo_claims)}")
        print(f"   Claims without GMIF: {len(regular_claims)}")

        print(f"\n📈 GMIF Distribution:")
        for level in sorted(gmif_dist.keys()):
            count = gmif_dist[level]
            bar = "█" * count
            print(f"   {level}: {bar} ({count})")

        print(f"\n🏛️ KNOWLEDGE ISLANDS:")
        if isinstance(self.agent_a, GriloFalanteAgent):
            if self.agent_a.islands:
                for island in self.agent_a.islands:
                    print(f"   - {island['id']}: {island['topic']} ({len(island['claims'])} claims)")
            else:
                print("   (none created yet)")

        return {
            "topic": self.topic,
            "rounds": self.rounds,
            "total_messages": len(self.conversation),
            "total_claims": len(self.all_claims),
            "gmif_distribution": gmif_dist,
            "conversation": [
                {
                    "agent": m.agent.value,
                    "content": m.content[:200],
                    "claims": m.claims_extracted,
                    "gaps": m.gaps_identified,
                }
                for m in self.conversation
            ],
        }


async def main():
    parser = argparse.ArgumentParser(description="AI-to-AI conversation test")
    parser.add_argument("--topic", "-t", default="Inteligência Artificial", help="Conversation topic")
    parser.add_argument("--rounds", "-r", type=int, default=3, help="Number of conversation rounds")
    parser.add_argument("--provider", "-p", default="ollama", help="LLM provider (ollama, openai, bitnet)")
    args = parser.parse_args()

    print(f"Using LLM provider: {args.provider}")

    llm_client = LLMClient(provider=args.provider)

    agent_a = GriloFalanteAgent("Grilo", llm_client)
    agent_b = RegularAgent("ChatGPT", llm_client)

    agent_a.create_island(args.topic)

    simulator = ConversationSimulator(
        agent_a=agent_a,
        agent_b=agent_b,
        topic=args.topic,
        rounds=args.rounds,
    )

    report = await simulator.run()

    print("\n" + "=" * 70)
    print("FULL CLAIMS LIST")
    print("=" * 70)
    for i, msg in enumerate(report.get("conversation", []), 1):
        for j, claim_text in enumerate(msg.get("claims", []), 1):
            print(f"{i}.{j}. {claim_text[:80]}...")

    report_file = f"conversation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\n📄 Report saved to: {report_file}")


if __name__ == "__main__":
    asyncio.run(main())