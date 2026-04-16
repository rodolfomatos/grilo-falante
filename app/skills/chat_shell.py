"""
Grilo Falante Chat Shell

Shell conversacional governada para /grilo chat.
"""

import asyncio
import logging
import json
import uuid
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict

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

    AUTO_SAVE_INTERVAL = 5
    SESSIONS_DIR = "/home/rodolfo/src/grilo_falante_v3.0/sessions"

    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or f"chat_{datetime.now().strftime('%y%m%d_%H%M%S')}"
        self.state = "INACTIVE"
        self.messages: List[ChatMessage] = []
        self.claims: List[Dict] = []
        self._message_count = 0
        self._cycle_id: Optional[str] = None
        self._loader = None
        self._acordar = None
        self._temporal_anchor: Optional[str] = None
        self._intention: Optional[str] = None
        self._governance_gate = None

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
        from grilo_falante.regime.governance_gate import GovernanceGate
        from grilo_falante.regime.pina import PINAProtocol

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

        pina = PINAProtocol(state_machine=self._loader.state_machine, ledger=ledger)
        self._governance_gate = GovernanceGate(pina_protocol=pina)

        temporal = temporal_anchor or datetime.now().strftime("%Y-%m-%d %H:%M")
        self._temporal_anchor = temporal
        self._intention = intention

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

    async def acordar_ilhas(
        self,
        tarefa: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Restaurar contexto das ilhas ao acordar.

        Usa o novo ciclo Acordar para carregar ilhas ativas
        e construir bundle de reentrada se houver tarefa.

        Args:
            tarefa: Tarefa opcional para construir bundle

        Returns:
            Contexto restaurado
        """
        try:
            from app.regime.acordar import acordar as ciclo_acordar

            resultado = await ciclo_acordar(
                session_id=self.session_id,
                tarefa=tarefa,
            )

            self._ilhas_ativas = resultado.ilhas_ativas
            self._ilhas_dormintes = resultado.ilhas_dormintes
            self._bundle = resultado.bundle

            return {
                "success": True,
                "ilhas_ativas": len(resultado.ilhas_ativas),
                "ilhas_dormintes": len(resultado.ilhas_dormintes),
                "bundle": resultado.bundle,
            }
        except Exception as e:
            logger.warning(f"acordar_ilhas failed: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def ir_dormir_ilhas(self) -> Dict[str, Any]:
        """
        Executar ciclo Ir Dormir - sanitização batch.

        Processa todas as interações desde o último acordar,
        identifica pedras, agrega em ilhas, e guarda estado.

        Returns:
            Relatório do ciclo de sono
        """
        try:
            from app.regime.dormir import ir_dormir

            interações = []
            for msg in self.messages:
                interações.append({
                    "tipo": "MENSAGEM",
                    "conteúdo": msg.content,
                    "role": msg.role,
                    "frequência": 0.5,
                    "intensidade": 0.3,
                    "novidade": 0.5,
                    "relevância": 0.4,
                })

            resultado = await ir_dormir(
                session_id=self.session_id,
                interações=interações,
            )

            return resultado

        except Exception as e:
            logger.warning(f"ir_dormir_ilhas failed: {e}")
            return {
                "success": False,
                "error": str(e),
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
            blocked_texts = [f"#{i+1}: {bc['text'][:50]}... ({', '.join(bc['issues'])})" for i, bc in enumerate(blocked_claims)]
            response_msg = (
                f"Governance gate: {len(blocked_claims)} claims requerem verificação:\n"
                + "\n".join(blocked_texts)
                + "\nEstas claims não serão incorporadas até verificação."
            )
        else:
            governance_passed = True
            response_msg = f"OK. {len(claims)} claims extraídas, governance passed."

        self.messages.append(message)
        self.claims.extend(claims)

        await self._store_claims(claims)

        if self._message_count % self.AUTO_SAVE_INTERVAL == 0:
            await self.save_to_file()

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

    def _check_governance(self, claims: List[Dict]) -> List[Dict]:
        """
        Verificar governance gate completo via GovernanceGate.

        Returns:
            Lista de dicts com claims bloqueadas e motivos
        """
        if self._governance_gate is None:
            logger.warning("GovernanceGate not initialized, using legacy check")
            return self._check_governance_legacy(claims)

        result = self._governance_gate.verify(claims)

        for candidate in result.pina_candidates:
            logger.info(f"PINA candidate: {candidate['nca_id']}")

        return result.blocked_claims

    def _check_governance_legacy(self, claims: List[Dict]) -> List[Dict]:
        """Legacy governance check for when GovernanceGate not available."""
        blocked = []
        for claim in claims:
            issues = []
            gmif_level = claim.get("gmif_level", "M3")
            text = claim.get("text", "")
            source = claim.get("source")

            if gmif_level in ["M5", "M6", "M7"]:
                if not source:
                    issues.append("nível M5+ requer fonte")

            if gmif_level in ["M6", "M7"]:
                if not source:
                    issues.append("nível M7/M6 requer evidência")

            if self._contradiz_claim_existente(text):
                issues.append("contradiz claim validada existente")

            text_lower = text.lower()
            if any(word in text_lower for word in ["obviamente", "claramente", "é óbvio", "é evidente que"]):
                issues.append("linguagem de fluência")

            if len(text) < 20 and gmif_level not in ["M1", "M2"]:
                issues.append("claim muito curta")

            if issues:
                blocked.append({
                    "claim_id": claim.get("id", "unknown"),
                    "text": text[:100],
                    "gmif_level": gmif_level,
                    "issues": issues,
                })

        return blocked

    def _contradiz_claim_existente(self, text: str) -> bool:
        """Verificar se texto contradiz alguma claim validada existente."""
        if not self.claims:
            return False

        text_lower = text.lower()
        negations = ["não é", "não existe", "não há", "não existe", "nunca", "jamais"]

        has_negation = any(neg in text_lower for neg in negations)
        if not has_negation:
            return False

        for existing in self.claims:
            if existing.get("legitimacy") == "ASSERTED":
                existing_text = existing.get("text", "").lower()
                has_existing_affirmation = not any(neg in existing_text for neg in negations)
                if has_existing_affirmation:
                    words_new = set(text_lower.split())
                    words_existing = set(existing_text.split())
                    overlap = words_new & words_existing
                    if len(overlap) > 3:
                        return True

        return False

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

    async def save_to_file(self) -> Dict[str, Any]:
        """Guardar sessão completa num ficheiro JSON."""
        os.makedirs(self.SESSIONS_DIR, exist_ok=True)

        session_data = {
            "session_id": self.session_id,
            "cycle_id": self._cycle_id,
            "state": self.state,
            "temporal_anchor": self._temporal_anchor,
            "intention": self._intention,
            "messages": [
                {
                    "role": m.role,
                    "content": m.content,
                    "timestamp": m.timestamp.isoformat(),
                    "claims": m.claims,
                    "gmif_level": m.gmif_level,
                }
                for m in self.messages
            ],
            "claims": self.claims,
            "saved_at": datetime.now().isoformat(),
        }

        filepath = os.path.join(self.SESSIONS_DIR, f"{self.session_id}.json")
        with open(filepath, "w") as f:
            json.dump(session_data, f, indent=2)

        return {
            "success": True,
            "filepath": filepath,
            "session_id": self.session_id,
        }

    @classmethod
    def load_from_file(cls, session_id: str) -> Optional["ChatShell"]:
        """Carregar sessão de um ficheiro JSON."""
        filepath = os.path.join(cls.SESSIONS_DIR, f"{session_id}.json")

        if not os.path.exists(filepath):
            logger.error(f"Session file not found: {filepath}")
            return None

        with open(filepath) as f:
            data = json.load(f)

        shell = cls(session_id=data["session_id"])
        shell._cycle_id = data.get("cycle_id")
        shell.state = data.get("state", "INACTIVE")
        shell._temporal_anchor = data.get("temporal_anchor")
        shell._intention = data.get("intention")

        shell.messages = [
            ChatMessage(
                role=m["role"],
                content=m["content"],
                timestamp=datetime.fromisoformat(m["timestamp"]),
                claims=m.get("claims", []),
                gmif_level=m.get("gmif_level", "M3"),
            )
            for m in data.get("messages", [])
        ]

        shell.claims = data.get("claims", [])
        shell._message_count = len(shell.messages)

        return shell

    def import_session(self, script: str) -> Dict[str, Any]:
        """
        Importar sessão a partir de um script bash ou JSON.

        Args:
            script: Script bash exportado ou JSON string

        Returns:
            Resultado do import
        """
        session_id = None
        cycle_id = None

        if script.strip().startswith("{"):
            try:
                data = json.loads(script)
                session_id = data.get("session_id")
                cycle_id = data.get("cycle_id")
            except json.JSONDecodeError:
                return {"success": False, "error": "Invalid JSON"}
        else:
            match = re.search(r'GRILO_SESSION_ID="([^"]+)"', script)
            if match:
                session_id = match.group(1)
            match = re.search(r'GRILO_CYCLE_ID="([^"]+)"', script)
            if match:
                cycle_id = match.group(1)

        if not session_id:
            return {"success": False, "error": "No session_id found in script"}

        loaded = self.load_from_file(session_id)
        if not loaded:
            return {
                "success": False,
                "error": f"Session {session_id} not found in {self.SESSIONS_DIR}",
                "hint": "Export the session first with grilo_export_session",
            }

        self.session_id = loaded.session_id
        self._cycle_id = loaded._cycle_id
        self.state = loaded.state
        self._temporal_anchor = loaded._temporal_anchor
        self._intention = loaded._intention
        self.messages = loaded.messages
        self.claims = loaded.claims
        self._message_count = loaded._message_count

        return {
            "success": True,
            "session_id": self.session_id,
            "cycle_id": self._cycle_id,
            "state": self.state,
            "messages_count": len(self.messages),
            "claims_count": len(self.claims),
        }

    def export_session(self) -> str:
        """
        Exportar sessão para retomar.

        Returns:
            Script bash + JSON data embedded
        """
        session_data = {
            "session_id": self.session_id,
            "cycle_id": self._cycle_id,
            "state": self.state,
            "temporal_anchor": self._temporal_anchor,
            "intention": self._intention,
            "messages": [
                {
                    "role": m.role,
                    "content": m.content,
                    "timestamp": m.timestamp.isoformat(),
                    "claims": m.claims,
                    "gmif_level": m.gmif_level,
                }
                for m in self.messages
            ],
            "claims": self.claims,
            "exported_at": datetime.now().isoformat(),
        }

        json_data = json.dumps(session_data, indent=2)

        script = f'''#!/bin/bash
# Grilo Falante Session Resume
# Session: {self.session_id}
# Cycle: {self._cycle_id}
# Date: {datetime.now().isoformat()}

export GRILO_SESSION_ID="{self.session_id}"
export GRILO_CYCLE_ID="{self._cycle_id}"

# JSON data (use grilo_import_session with this data)
export GRILO_SESSION_JSON=\'{json_data}\'

echo "Resuming Grilo Falante session: {self.session_id}"
echo "Cycle: {self._cycle_id}"
echo "Messages: {len(self.messages)}"
echo ""
echo "To resume, use:"
echo "  grilo chat --session {self.session_id}"
echo "  grilo chat --import-json \\$GRILO_SESSION_JSON"
'''

        return script

    async def end(self) -> Dict[str, Any]:
        """
        Terminar sessão - grilo_vai_dormir().

        Executa o ciclo Ir Dormir para sanitizar as interações
        do dia antes de hibernar.

        Returns:
            Resultado do shutdown
        """
        if self._acordar is None:
            return {"success": False, "message": "No active session"}

        dormir_result = await self.ir_dormir_ilhas()

        vai_dormir_result = self._acordar.vai_dormir()

        self.state = "HIBERNATED"

        save_data = await self.save_to_file()

        return {
            "success": vai_dormir_result.get("success", False),
            "message": vai_dormir_result.get("message", ""),
            "session_id": self.session_id,
            "cycle_id": self._cycle_id,
            "dormir_result": dormir_result,
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
