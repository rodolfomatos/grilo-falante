"""
Unified Chat API - Unified interface for Grilo Falante domain plugins.

This module provides:
- Automatic plugin routing based on query content
- Session management for multi-turn dialogues
- Unified FastAPI endpoints for all domain plugins

Usage:
    from grilo_chat_api import ChatAPIService, UnifiedRouter

    api = ChatAPIService()
    result = await api.process_message(
        query="Como funciona a matrícula?",
        user_id="user123",
        session_id="session456",
    )
"""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ChatSession:
    """Represents a chat session."""
    session_id: str
    user_id: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    messages: List[Dict[str, Any]] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    active_domain: Optional[str] = None
    escalation_active: bool = False


@dataclass
class ChatMessage:
    """A single chat message."""
    message_id: str
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    domain: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RoutingResult:
    """Result of routing a query to a domain."""
    domain: str
    confidence: float
    reason: str
    adapter_name: str


class UnifiedRouter:
    """
    Routes queries to the appropriate domain plugin.

    Uses keyword matching and LLM-assisted classification
    to determine which plugin should handle the query.
    """

    def __init__(self):
        self._routing_cache: Dict[str, str] = {}
        self._llm_classifier_available = False

    def route(self, query: str, context: Optional[Dict[str, Any]] = None) -> RoutingResult:
        """
        Route a query to the appropriate domain.

        Args:
            query: User's query
            context: Optional context (previous domain, user preferences)

        Returns:
            RoutingResult with domain and confidence
        """
        from grilo_falante.platform import PluginRegistry

        query_lower = query.lower()

        if context and context.get("active_domain"):
            domain_confidence = self._check_domain_relevance(
                query, context["active_domain"]
            )
            if domain_confidence > 0.6:
                return RoutingResult(
                    domain=context["active_domain"],
                    confidence=domain_confidence,
                    reason="Consistent with active domain",
                    adapter_name=context["active_domain"],
                )

        all_keywords = PluginRegistry.get_all_routing_keywords()

        best_domain = None
        best_score = 0
        best_reason = ""

        for plugin_name, routing_config in all_keywords.items():
            score, reason = self._calculate_routing_score(query_lower, routing_config)
            if score > best_score:
                best_score = score
                best_domain = plugin_name
                best_reason = reason

        if best_score > 0:
            return RoutingResult(
                domain=best_domain,
                confidence=best_score,
                reason=best_reason,
                adapter_name=best_domain,
            )

        return RoutingResult(
            domain="general",
            confidence=0.5,
            reason="No specific domain matched",
            adapter_name="general",
        )

    def _calculate_routing_score(
        self, query_lower: str, routing_config: Dict[str, List[str]]
    ) -> tuple[float, str]:
        """
        Calculate routing score for a query against a routing config.
        """
        max_score = 0
        matched_keywords = []

        for category, keywords in routing_config.items():
            for keyword in keywords:
                if keyword.lower() in query_lower:
                    score = len(keyword) / max(len(keyword), 10)
                    if score > max_score:
                        max_score = score
                    matched_keywords.append(keyword)

        if matched_keywords:
            return max_score, f"Matched: {', '.join(matched_keywords[:3])}"

        return 0, "No keywords matched"

    def _check_domain_relevance(self, query: str, domain: str) -> float:
        """Check if query is still relevant to active domain."""
        from grilo_falante.platform import PluginRegistry

        try:
            adapter = PluginRegistry.get(domain)
            routing_config = adapter.get_routing_config()

            query_lower = query.lower()
            for category, keywords in routing_config.items():
                for keyword in keywords:
                    if keyword.lower() in query_lower:
                        return 0.7

            return 0.3

        except Exception:
            return 0.3


class ChatAPIService:
    """
    Unified Chat API service.

    Provides a single interface for:
    - Query routing to domain plugins
    - Session management
    - Multi-turn conversation context
    - Escalation handling
    """

    def __init__(self):
        self.router = UnifiedRouter()
        self._sessions: Dict[str, ChatSession] = {}

    def create_session(
        self,
        user_id: str,
        domain: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> ChatSession:
        """
        Create a new chat session.

        Args:
            user_id: User identifier
            domain: Optional initial domain
            context: Optional initial context

        Returns:
            ChatSession object
        """
        session_id = str(uuid.uuid4())
        session = ChatSession(
            session_id=session_id,
            user_id=user_id,
            active_domain=domain,
            context=context or {},
        )
        self._sessions[session_id] = session
        logger.info(f"Created session {session_id} for user {user_id}")
        return session

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get an existing session."""
        return self._sessions.get(session_id)

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        domain: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[ChatMessage]:
        """Add a message to a session."""
        session = self._sessions.get(session_id)
        if not session:
            return None

        message = ChatMessage(
            message_id=str(uuid.uuid4()),
            role=role,
            content=content,
            domain=domain,
            metadata=metadata or {},
        )

        session.messages.append({
            "message_id": message.message_id,
            "role": message.role,
            "content": message.content,
            "timestamp": message.timestamp.isoformat(),
            "domain": message.domain,
            "metadata": message.metadata,
        })

        session.updated_at = datetime.now()

        if role == "assistant" and domain:
            session.active_domain = domain

        return message

    async def process_message(
        self,
        query: str,
        user_id: str,
        session_id: Optional[str] = None,
        domain_hint: Optional[str] = None,
        llm_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process a user message and return a response.

        Args:
            query: User's message
            user_id: User identifier
            session_id: Optional existing session ID
            domain_hint: Optional hint for routing
            llm_config: LLM configuration

        Returns:
            Dict with response and metadata
        """
        from grilo_falante.platform import PluginRegistry

        if session_id:
            session = self.get_session(session_id)
        else:
            session = None

        if not session:
            session = self.create_session(user_id=user_id)

        context = self._build_context(session)

        if domain_hint:
            routing_result = RoutingResult(
                domain=domain_hint,
                confidence=1.0,
                reason="Domain hint provided",
                adapter_name=domain_hint,
            )
        else:
            routing_result = self.router.route(query, context)

        self.add_message(
            session_id=session.session_id,
            role="user",
            content=query,
            domain=routing_result.domain,
        )

        try:
            adapter = PluginRegistry.get(routing_result.domain)
        except ValueError:
            logger.warning(f"No adapter found for domain: {routing_result.domain}")
            response_text = (
                "Desculpe, não consigo processar esta questão no momento. "
                "Por favor, tente novamente ou contacte suporte."
            )
            adapter = None

        if adapter:
            result = await adapter.process_query(
                query=query,
                context=context,
                llm_config=llm_config or {"provider": "bitnet"},
            )

            response_text = result.response
            response_metadata = {
                "domain": result.domain,
                "confidence": result.confidence,
                "escalation_triggered": result.escalation_triggered,
                "routing_confidence": routing_result.confidence,
            }

            if result.escalation_triggered:
                session.escalation_active = True
                response_metadata["escalation_reason"] = result.escalation_reason
        else:
            response_text = "Plugin não disponível."
            response_metadata = {}

        self.add_message(
            session_id=session.session_id,
            role="assistant",
            content=response_text,
            domain=routing_result.domain,
            metadata=response_metadata,
        )

        return {
            "response": response_text,
            "session_id": session.session_id,
            "domain": routing_result.domain,
            "confidence": routing_result.confidence,
            "escalation_triggered": session.escalation_active,
            "message_count": len(session.messages),
            "metadata": response_metadata,
        }

    def _build_context(self, session: ChatSession) -> Dict[str, Any]:
        """Build context for LLM from session history."""
        context = dict(session.context)

        recent_messages = session.messages[-10:] if session.messages else []
        context["recent_messages"] = [
            {"role": m["role"], "content": m["content"]}
            for m in recent_messages
        ]

        context["active_domain"] = session.active_domain
        context["escalation_active"] = session.escalation_active

        return context

    def list_sessions(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all sessions, optionally filtered by user."""
        sessions = []
        for session in self._sessions.values():
            if user_id is None or session.user_id == user_id:
                sessions.append({
                    "session_id": session.session_id,
                    "user_id": session.user_id,
                    "created_at": session.created_at.isoformat(),
                    "updated_at": session.updated_at.isoformat(),
                    "message_count": len(session.messages),
                    "active_domain": session.active_domain,
                    "escalation_active": session.escalation_active,
                })
        return sessions


class GlobalChatAPI:
    """
    Global chat API instance for the application.
    """
    _instance: Optional[ChatAPIService] = None

    @classmethod
    def get_instance(cls) -> ChatAPIService:
        if cls._instance is None:
            cls._instance = ChatAPIService()
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None
