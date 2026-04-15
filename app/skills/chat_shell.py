"""
Grilo Falante Chat Shell

Shell conversacional governada para /grilo chat.
"""

import asyncio
import logging
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ChatMessage:
    """Uma mensagem no chat governado."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    claims: List[Dict] = field(default_factory=list)
    gmif_level: str = "M3"


@dataclass
class ChatResponse:
    """Resposta do chat governado."""
    message: str
    claims_extracted: int
    gmif_summary: Dict[str, int]
    governance_passed: bool
    blocked_claims: List[str] = field(default_factory=list)
    session_id: str = ""


class ChatShell:
    """
    Shell conversacional governada.

    Fluxo:
    1. start() → grilo_load() + grilo_acordar()
    2. send_message() → extract claims → classify GMIF → governance check
    3. end() → grilo_vai_dormir()

    Armazenamento:
    - MemPalace (wing_conversas): cache semântico rápido
    - PostgreSQL: claims autoritativas
    """

    AUTO_SAVE_INTERVAL = 5  # mensagens

    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or f"chat_{datetime.now().strftime('%y%m%d_%H%M%S')}"
        self.state = "INACTIVE"
        self.messages: List[ChatMessage] = []
        self.claims: List[Dict] = []
        self._message_count = 0
        self._cycle_id: Optional[str] = None
        self._loader = None
        self._acordar = None

    async def start(
        self,
        temporal_anchor: Optional[str] = None,
        intention: str = "Governed chat session",
        mode: str = "exploratory",
    ) -> Dict[str, Any]:
        """
        Iniciar sessão governada.

        Args:
            temporal_anchor: Data/hora (default: now)
            intention: Intenção da sessão
            mode: "exploratory" or "committed"

        Returns:
            Dicionário com estado inicial
        """
        if self.state != "INACTIVE":
            return {
                "success": False,
                "message": f"Cannot start - already in state {self.state}",
                "state": self.state,
            }

        from grilo_falante.regime import Loader, Acordar, Ledger

        ledger = Ledger()
        self._loader = Loader(ledger=ledger)

        load_result = self._loader.load()
        if not load_result.success:
            return {
                "success": False,
                "message": f"Load failed: {load_result.message}",
            }

        self._cycle_id = load_result.cycle_id
        self._acordar = Acordar(
            state_machine=self._loader.state_machine,
            ledger=ledger,
        )

        temporal = temporal_anchor or datetime.now().strftime("%Y-%m-%d %H:%M")

        acordar_result = self._acordar.execute(
            temporal_anchor=temporal,
            intention=intention,
            mode=mode,
        )

        if acordar_result.success:
            self.state = "GOVERNING"
        else:
            self.state = "LOADED"

        return {
            "success": True,
            "state": self.state,
            "cycle_id": self._cycle_id,
            "temporal_anchor": acordar_result.temporal_anchor,
            "intention_declared": acordar_result.intention_declared,
            "session_id": self.session_id,
        }

    async def send_message(self, content: str, role: str = "user") -> ChatResponse:
        """
        Enviar mensagem com governance check.

        Args:
            content: Texto da mensagem
            role: "user" ou "assistant"

        Returns:
            ChatResponse com análise
        """
        if self.state not in ("GOVERNING", "LOADED", "ACTIVE"):
            return ChatResponse(
                message=f"Cannot send message - regime not active (state: {self.state}). Call start() first.",
                claims_extracted=0,
                gmif_summary={},
                governance_passed=False,
            )

        self._message_count += 1

        timestamp = datetime.now()
        message = ChatMessage(role=role, content=content, timestamp=timestamp)

        claims = await self._extract_claims(content, role)
        message.claims = claims

        gmif_summary = self._summarize_gmif(claims)
        for claim in claims:
            claim["gmif_level"] = gmif_summary.get(claim.get("type", "unknown"), "M3")

        message.gmif_level = self._determine_message_gmif(gmif_summary)

        blocked_claims = self._check_governance(claims)

        if blocked_claims:
            governance_passed = False
            response_msg = (
                f"Mensagem contém claims que requerem verificação humana:\n"
                f"{', '.join(blocked_claims)}\n"
                f"Estas claims não serão incorporadas até verificação."
            )
        else:
            governance_passed = True
            response_msg = f"OK. {len(claims)} claims extraídas."

        self.messages.append(message)
        self.claims.extend(claims)

        await self._store_claims(claims)

        if self._message_count % self.AUTO_SAVE_INTERVAL == 0:
            await self.save()

        return ChatResponse(
            message=response_msg,
            claims_extracted=len(claims),
            gmif_summary=gmif_summary,
            governance_passed=governance_passed,
            blocked_claims=blocked_claims,
            session_id=self.session_id,
        )

    async def _extract_claims(self, content: str, role: str) -> List[Dict]:
        """Extrair claims da mensagem."""
        from app.data.memory.graph.claims import ClaimsExtractor

        extractor = ClaimsExtractor()

        messages = [{"role": role, "content": content}]
        claims = extractor.extract_from_chat(messages, self.session_id)

        return [
            {
                "id": c.id,
                "text": c.text,
                "type": c.type,
                "anchors": c.anchors,
                "role": role,
                "timestamp": datetime.now().isoformat(),
            }
            for c in claims
        ]

    def _summarize_gmif(self, claims: List[Dict]) -> Dict[str, int]:
        """Sumarizar distribuição GMIF dos claims."""
        summary: Dict[str, int] = {}
        for claim in claims:
            ctype = claim.get("type", "unknown")
            summary[ctype] = summary.get(ctype, 0) + 1
        return summary

    def _determine_message_gmif(self, gmif_summary: Dict[str, int]) -> str:
        """Determinar nível GMIF da mensagem."""
        if "fact" in gmif_summary:
            return "M5"  # Uma fonte
        if "claim" in gmif_summary:
            return "M3"  # Parcial
        return "M3"

    def _check_governance(self, claims: List[Dict]) -> List[str]:
        """Verificar governance gate - retorna lista de claims bloqueadas."""
        blocked = []
        for claim in claims:
            text = claim.get("text", "").lower()
            if any(word in text for word in ["obviamente", "claramente", "é óbvio"]):
                blocked.append(f"Blocking pattern: {claim.get('text', '')[:50]}")
        return blocked

    async def _store_claims(self, claims: List[Dict]) -> None:
        """Guardar claims em MemPalace e PostgreSQL."""
        if not claims:
            return

        try:
            from grilo_falante.backend.memory import MemPalaceCache, MEMPALACE_AVAILABLE

            if MEMPALACE_AVAILABLE:
                cache = MemPalaceCache()
                await cache.store_batch(claims)

            logger.info(f"Stored {len(claims)} claims in MemPalace")
        except Exception as e:
            logger.warning(f"Failed to store in MemPalace: {e}")

        try:
            from grilo_falante.backend.db.repositories import ClaimRepository
            from grilo_falante.models import GovernedClaim, GMIFLevel

            repo = ClaimRepository()

            for claim in claims:
                governed_claim = GovernedClaim(
                    claim_key=claim.get("id", f"CLM-{uuid.uuid4().hex[:8]}"),
                    claim_text=claim.get("text", ""),
                    gmif_level=GMIFLevel.M4_DOUBTFUL,
                    gmif_confidence=0.5,
                    source_id=None,
                    session_id=self.session_id,
                )
                await repo.create(governed_claim)

            logger.info(f"Stored {len(claims)} claims in PostgreSQL")
        except Exception as e:
            logger.warning(f"Failed to store in PostgreSQL: {e}")

    async def save(self) -> Dict[str, Any]:
        """Guardar sessão manualmente."""
        return {
            "session_id": self.session_id,
            "cycle_id": self._cycle_id,
            "state": self.state,
            "messages_count": len(self.messages),
            "claims_count": len(self.claims),
            "saved_at": datetime.now().isoformat(),
        }

    def export_session(self) -> str:
        """
        Exportar sessão para retomar.

        Returns:
            Script bash para source
        """
        script = f'''#!/bin/bash
# Grilo Falante Session Resume
# Session: {self.session_id}
# Cycle: {self._cycle_id}
# Date: {datetime.now().isoformat()}

export GRILO_SESSION_ID="{self.session_id}"
export GRILO_CYCLE_ID="{self._cycle_id}"

echo "Resuming Grilo Falante session: {self.session_id}"
echo "Cycle: {self._cycle_id}"
echo ""
echo "To resume, use:"
echo "  grilo chat --session {self.session_id}"
'''

        return script

    async def end(self) -> Dict[str, Any]:
        """
        Terminar sessão - grilo_vai_dormir().

        Returns:
            Resultado do shutdown
        """
        if self._acordar is None:
            return {"success": False, "message": "No active session"}

        vai_dormir_result = self._acordar.vai_dormir()

        self.state = "HIBERNATED"

        save_data = await self.save()

        return {
            "success": vai_dormir_result.get("success", False),
            "message": vai_dormir_result.get("message", ""),
            "session_id": self.session_id,
            "cycle_id": self._cycle_id,
            "stats": save_data,
        }

    def get_status(self) -> Dict[str, Any]:
        """Obter estado atual da sessão."""
        return {
            "session_id": self.session_id,
            "cycle_id": self._cycle_id,
            "state": self.state,
            "messages_count": len(self.messages),
            "claims_count": len(self.claims),
            "last_message": self.messages[-1].content[:100] if self.messages else None,
        }
