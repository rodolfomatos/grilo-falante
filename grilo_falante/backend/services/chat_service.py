"""Chat Service — Message processing and streaming"""

import asyncio
import hashlib
import json
import re
import time
import uuid
from datetime import datetime
from typing import AsyncGenerator, Optional

from grilo_falante.backend.db.connection import acquire_connection
from grilo_falante.backend.db.repositories import (
    ConversationRepository,
    MessageRepository,
    ClaimRepository,
    GapRepository,
)
from grilo_falante.backend.services.llm import get_llm_service
from grilo_falante.backend.services.llm.base import LLMMessage
from grilo_falante.backend.services.query import QueryPipeline
from grilo_falante.backend.memory.vector_index import VectorIndex
from grilo_falante.models import Conversation, Message, GMIFLevel, Gap
from grilo_falante.config import settings


def generate_key(prefix: str = "") -> str:
    """Generate a unique key."""
    uuid_str = str(uuid.uuid4())[:12]
    return f"{prefix}:{uuid_str}" if prefix else uuid_str


def content_hash(content: str) -> str:
    """Generate a short hash for content."""
    return hashlib.sha256(content.encode()).hexdigest()[:12]


class ChatService:
    """Service for processing chat messages with epistemic governance."""

    def __init__(self):
        self.conversation_repo = ConversationRepository()
        self.message_repo = MessageRepository()
        self.claim_repo = ClaimRepository()
        self.gap_repo = GapRepository()
        self._llm_service = None
        self.query_pipeline = QueryPipeline()

    @property
    def llm_service(self):
        """Lazy-load LLM service only when needed."""
        if self._llm_service is None:
            self._llm_service = get_llm_service()
        return self._llm_service

    async def create_conversation(
        self,
        user_id: str = "anonymous",
        title: str = "New Conversation",
        model: Optional[str] = None,
    ) -> Conversation:
        """Create a new conversation."""
        conversation_key = generate_key("conv")
        model_used = model or "default"
        row = await self.conversation_repo.create(
            conversation_key=conversation_key,
            user_id=user_id,
            title=title,
            model_used=model_used,
        )
        return Conversation(
            id=row["id"],
            conversation_key=row["conversation_key"],
            title=row["title"],
            user_id=row["user_id"],
            model_used=row["model_used"],
            message_count=0,
            created_at=row["created_at"],
        )

    async def get_conversation(self, conversation_key: str) -> Optional[Conversation]:
        """Get a conversation by key."""
        row = await self.conversation_repo.get_by_key(conversation_key)
        if not row:
            return None
        return Conversation(
            id=row["id"],
            conversation_key=row["conversation_key"],
            title=row["title"],
            user_id=row["user_id"],
            model_used=row["model_used"],
            message_count=row["message_count"],
            claims_count=row["claims_count"],
            gaps_count=row["gaps_count"],
            is_archived=row["is_archived"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            last_message_at=row["last_message_at"],
        )

    async def list_conversations(
        self, user_id: str = "anonymous", limit: int = 50
    ) -> list[Conversation]:
        """List conversations for a user."""
        rows = await self.conversation_repo.list_by_user(user_id, limit=limit)
        return [
            Conversation(
                id=row["id"],
                conversation_key=row["conversation_key"],
                title=row["title"],
                user_id=row["user_id"],
                model_used=row["model_used"],
                message_count=row["message_count"],
                claims_count=row["claims_count"],
                gaps_count=row["gaps_count"],
                is_archived=row["is_archived"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                last_message_at=row["last_message_at"],
            )
            for row in rows
        ]

    async def get_messages(self, conversation_key: str) -> list[Message]:
        """Get messages for a conversation."""
        conversation = await self.get_conversation(conversation_key)
        if not conversation:
            return []
        rows = await self.message_repo.get_by_conversation(conversation.id)
        return [
            Message(
                id=row["id"],
                message_key=row["message_key"],
                conversation_id=row["conversation_id"],
                role=row["role"],
                content=row["content"],
                model=row["model"],
                tokens_used=row["tokens_used"],
                inference_time_ms=row["inference_time_ms"],
                claims_detected=list(row["claims_detected"] or []),
                gaps_identified=list(row["gaps_identified"] or []),
                gmif_level=row["gmif_level"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    async def process_message_streaming(
        self,
        conversation_key: str,
        message: str,
        user_id: str = "anonymous",
    ) -> AsyncGenerator[dict, None]:
        """
        Process a message and stream the response.

        NEW FLOW:
        1. Store user message
        2. Check local RAG knowledge (vector search)
        3. If no relevant context → emit gap + "Ainda tenho de confirmar"
        4. Generate LLM response
        5. Extract claims from RESPONSE (not user message)
        6. Store assistant message
        7. Background: verify claims against sources

        Yields events:
        - {"type": "gap", "data": {...}} (if knowledge gap detected)
        - {"type": "chunk", "data": {"content": "..."}}
        - {"type": "done", "data": {...}}
        """
        # Get or create conversation
        conversation = await self.get_conversation(conversation_key)
        if not conversation:
            conversation = await self.create_conversation(
                user_id=user_id,
                title=self._generate_title(message),
            )

        # Store user message
        user_message_key = generate_key("msg")
        start_time = time.time()

        user_msg_row = await self.message_repo.create(
            message_key=user_message_key,
            conversation_id=conversation.id,
            role="user",
            content=message,
        )

        yield {"type": "info", "data": {"message_key": user_message_key}}

        # Step 1: Check local RAG knowledge (vector similarity)
        has_local_knowledge = False
        gap_detected = False
        rag_context = ""

        try:
            vector_index = VectorIndex()
            query_embedding = await vector_index.embed_text(message)
            similar_claims = await vector_index.search(query_embedding, limit=5, match_threshold=0.6)

            if similar_claims:
                has_local_knowledge = True
                rag_context = self._build_rag_context(similar_claims)
            else:
                gap_detected = True
                gap = await self._create_gap_from_message(message, conversation.conversation_key)
                yield {"type": "gap", "data": gap.to_dict()}
        except Exception as e:
            rag_context = ""
            gap_detected = True
            gap = await self._create_gap_from_message(message, conversation.conversation_key)
            yield {"type": "gap", "data": gap.to_dict()}

        # Step 2: Get conversation history context
        context_messages = await self.get_messages(conversation.conversation_key)
        history_context = self._build_context(context_messages)

        # Step 3: Build prompt with RAG context
        model = conversation.model_used or self.llm_service.name

        response_content = ""
        response_key = generate_key("msg")

        # Build user message with context
        if gap_detected:
            user_prompt = f"[Nota: Esta é uma pergunta sobre conhecimento que não consigo verificar localmente. Indica claramente quando não tens certeza.]\n\nContexto relevante:\n{rag_context}\n\nHistórico:\n{history_context}\n\nPergunta: {message}"
        elif rag_context:
            user_prompt = f"Contexto relevante do conhecimento local:\n{rag_context}\n\nHistórico:\n{history_context}\n\nPergunta: {message}"
        else:
            user_prompt = f"Histórico:\n{history_context}\n\nPergunta: {message}"

        messages = [LLMMessage(role="user", content=user_prompt)]

        # Step 4: Generate response with streaming
        async for chunk in self.llm_service.stream(messages=messages):
            if isinstance(chunk, str):
                response_content += chunk
                yield {"type": "chunk", "data": {"content": chunk}}
            else:
                content = chunk.content if hasattr(chunk, 'content') else str(chunk)
                response_content += content
                yield {"type": "chunk", "data": {"content": content}}

        # Step 5: Extract claims from RESPONSE (not from user message)
        claims_created = await self._extract_claims_from_response(
            response_content,
            conversation.conversation_key,
        )

        for claim in claims_created:
            yield {"type": "claim", "data": claim.model_dump(mode='json')}

        # Calculate stats
        inference_time = int((time.time() - start_time) * 1000)
        tokens_estimate = len(response_content) // 4  # rough estimate

        # Step 6: Store assistant message
        assistant_msg_row = await self.message_repo.create(
            message_key=response_key,
            conversation_id=conversation.id,
            role="assistant",
            content=response_content,
            model=model,
            tokens_used=tokens_estimate,
            inference_time_ms=inference_time,
            claims_detected=[c.id for c in claims_created] if claims_created else [],
            gaps_identified=[g.id for g in []] if gap_detected else [],
        )

        # Link claims to message
        if claims_created:
            await self.message_repo.link_claims(
                assistant_msg_row["id"],
                [c.id for c in claims_created]
            )
            await self.conversation_repo.update_stats(
                conversation.conversation_key,
                claims_count=len(claims_created),
            )

        # Update conversation timestamp
        await self.conversation_repo.update_last_message(conversation.conversation_key)

        yield {
            "type": "done",
            "data": {
                "message_key": response_key,
                "conversation_key": conversation.conversation_key,
                "tokens": tokens_estimate,
                "time_ms": inference_time,
                "claims_count": len(claims_created),
                "gaps_count": 1 if gap_detected else 0,
            },
        }

        # Step 7: Background re-evaluation (async)
        asyncio.create_task(self._background_reevaluation(conversation.id))

    def _classify_intent(self, message: str) -> str:
        """Classify message intent."""
        message_lower = message.lower().strip()

        # Question indicators
        question_words = ["what", "who", "where", "when", "why", "how", "is", "are", "do", "does", "can", "?", "explain"]
        if any(message_lower.startswith(w) or message_lower.endswith(w) for w in question_words):
            return "question"

        # Command indicators
        command_words = ["show", "tell", "list", "create", "delete", "generate", "write", "calculate"]
        if any(message_lower.startswith(w) for w in command_words):
            return "command"

        # Creative indicators
        creative_words = ["write", "create", "imagine", "story", "poem", "song", "invent"]
        if any(w in message_lower for w in creative_words):
            return "creative"

        # Default to statement (factual claim potential)
        return "statement"

    async def _extract_claims(self, message: str, session_id: str) -> list:
        """Extract claims from a message."""
        from grilo_falante.models import GovernedClaim, ClaimType, GMIFLevel
        from grilo_falante.backend.db.repositories import generate_gfid

        claims = []

        # Simple heuristic: look for factual statements
        # This would be replaced with actual LLM-based extraction
        factual_patterns = [
            r"(\w+\s+is\s+\w+)",
            r"(\w+\s+was\s+\w+)",
            r"(\w+\s+were\s+\w+)",
            r"(\d+\s+(?:years?|days?|months?|centuries?|decades?)\s+ago)",
            r"(the\s+\w+\s+\w+\s+\w+)",
        ]

        for pattern in factual_patterns:
            matches = re.finditer(pattern, message, re.IGNORECASE)
            for match in matches:
                claim_text = match.group(1).strip()
                if len(claim_text) > 10 and len(claim_text) < 500:
                    claim_key = generate_key("claim")
                    hash_cont = content_hash(claim_text)

                    claim = GovernedClaim(
                        claim_key=claim_key,
                        claim_text=claim_text,
                        claim_type=ClaimType.CORE_CLAIM,
                        session_id=session_id,
                        gmif_level=GMIFLevel.M3_PARTIAL,
                        gmif_confidence=0.5,
                        provenance={"source": "chat", "match": pattern},
                        gfid=generate_gfid(hash_cont, "M3", "chat"),
                    )

                    created = await self.claim_repo.create(claim)
                    claims.append(created)

        return claims

    async def _identify_gaps(self, message: str, session_id: str) -> list:
        """Identify knowledge gaps from a message."""
        from grilo_falante.models import Gap, GapType

        gaps = []

        # Look for explicit unknowns in the message
        unknown_patterns = [
            r"i(?:'m| am) not sure (?:about|if|when|how)",
            r"i don't know",
            r"uncertain",
            r"unknown",
            r"not clear",
            r"what about (\w+)",
            r"but what (?:\w+\s+){0,3}\?",
        ]

        for pattern in unknown_patterns:
            matches = re.finditer(pattern, message, re.IGNORECASE)
            for match in matches:
                gap_text = match.group(0).strip()
                gap_key = generate_key("gap")

                gap = Gap(
                    gap_key=gap_key,
                    gap_type=GapType.TIPO_A_FAILURE,
                    query=message[:100],
                    reason=f"User expressed uncertainty: {gap_text}",
                    expected_claim=f"Clarification needed: {gap_text}",
                )

                created = await self.gap_repo.create(gap)
                gaps.append(created)

        # Also look for implicit gaps - questions that imply missing knowledge
        if "?" in message and len(gaps) == 0:
            gap_key = generate_key("gap")
            gap = Gap(
                gap_key=gap_key,
                gap_type=GapType.TIPO_A_FAILURE,
                query=message[:100],
                reason="Question that requires knowledge to answer",
                expected_claim=None,
            )
            created = await self.gap_repo.create(gap)
            gaps.append(created)

        return gaps

    async def _create_gap_from_message(self, message: str, session_id: str) -> Gap:
        """Create a gap when no local knowledge is available."""
        from grilo_falante.models import GapType, GapStatus

        gap_key = generate_key("gap")

        gap = Gap(
            gap_key=gap_key,
            gap_type=GapType.TIPO_A_FAILURE,
            query=message[:100] if len(message) > 100 else message,
            reason="No local knowledge available to verify this claim",
            expected_claim=None,
            status=GapStatus.IDENTIFIED,
        )

        created = await self.gap_repo.create(gap)
        return created

    async def _extract_claims_from_response(
        self,
        response: str,
        session_id: str,
    ) -> list:
        """Extract claims from LLM response text."""
        from grilo_falante.models import GovernedClaim, ClaimType, GMIFLevel, ValidationState, LegitimacyState
        from grilo_falante.backend.db.repositories import generate_gfid

        claims = []

        # Patterns for factual statements in response
        factual_patterns = [
            r"([A-Z][a-z]+(?:\s+[a-z]+)*\s+(?:was|were|is|are)\s+(?:\w+\s+){0,10}(?:in|of|for|because|since)\s+\w+)",
            r"(The\s+\w+(?:\s+\w+)*\s+(?:is|was|are|were)\s+(?:\w+\s+){0,10}(?:\w+\.))",
            r"([A-Z][a-z]+(?:\s+[a-z]+)*\s+(?:lived|worked|created|discovered|invented)\s+(?:\w+\s+){0,10}(?:\w+\.))",
            r"(\d+(?:\s+(?:years?|days?|months?|centuries?|decades?))\s+ago)",
            r"(The\s+\w+(?:\s+\w+){0,5}\s+(?:was|were)\s+(?:known|believed|considered)\s+as\s+\w+)",
        ]

        seen_hashes = set()

        for pattern in factual_patterns:
            matches = re.finditer(pattern, response, re.IGNORECASE)
            for match in matches:
                claim_text = match.group(1).strip()

                # Skip if too short or too long
                if len(claim_text) < 10 or len(claim_text) > 500:
                    continue

                # Check for duplicates
                content_h = content_hash(claim_text)
                if content_h in seen_hashes:
                    continue
                seen_hashes.add(content_h)

                claim_key = generate_key("claim")

                claim = GovernedClaim(
                    claim_key=claim_key,
                    claim_text=claim_text,
                    claim_type=ClaimType.CORE_CLAIM,
                    session_id=session_id,
                    gmif_level=GMIFLevel.UNVERIFIED,  # Default to unverified until background check
                    gmif_confidence=0.5,
                    attribution="llm_response",
                    epistemic_role="descriptive",
                    legitimacy_state=LegitimacyState.UNVALIDATED,
                    validation_status=ValidationState.PENDING,
                    provenance={
                        "source": "llm_response",
                        "pattern": pattern,
                        "confidence": 0.5,
                    },
                    gfid=generate_gfid(content_h, "M2", "chat"),
                )

                try:
                    created = await self.claim_repo.create(claim)
                    claims.append(created)

                    # Also create embedding for the claim
                    try:
                        vector_index = VectorIndex()
                        await vector_index.add_claim_embedding(created.id, claim_text)
                    except Exception:
                        pass  # Don't fail if embedding creation fails

                except Exception as e:
                    continue  # Skip duplicates

        return claims

    def _build_rag_context(self, similar_claims: list[dict]) -> str:
        """Build context text from similar claims for RAG."""
        if not similar_claims:
            return ""

        context_parts = ["=== Conhecimento Local Verificado ==="]

        for i, claim in enumerate(similar_claims[:5], 1):
            claim_text = claim.get("claim_text", "")
            gmif_level = claim.get("gmif_level", "UNKNOWN")
            similarity = claim.get("similarity", 0)

            context_parts.append(
                f"{i}. {claim_text}\n"
                f"   [GMIF: {gmif_level}, Similarity: {similarity:.2f}]"
            )

        context_parts.append("=" * 40)

        return "\n".join(context_parts)

    def _build_context(self, messages: list[Message]) -> str:
        """Build context text from conversation history."""
        if not messages:
            return ""

        context_parts = []
        for msg in messages[-10:]:
            role = "User" if msg.role == "user" else "Assistant"
            context_parts.append(f"{role}: {msg.content}")

        return "\n\n".join(context_parts)

    def _generate_title(self, message: str) -> str:
        """Generate a conversation title from the first message."""
        # Simple: take first 50 chars
        title = message[:50]
        if len(message) > 50:
            title += "..."
        return title

    async def _background_reevaluation(self, conversation_id: int) -> None:
        """Background task to re-evaluate previous claims."""
        try:
            # Get claims from conversation
            claims = await self.message_repo.get_recent_claims(conversation_id, limit=20)

            # For each claim, re-check with current knowledge
            for claim_row in claims:
                # This would trigger the Grilo Falante governance loop
                # For now, just log
                pass

        except Exception as e:
            # Log but don't fail
            pass