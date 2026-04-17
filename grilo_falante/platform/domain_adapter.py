"""
Domain Adapter - Abstract base class for Grilo Falante plugins.

This module defines the interface that all domain plugins must implement
to be compatible with the Grilo Falante platform.

Usage:
    from grilo_falante.platform.domain_adapter import DomainAdapter, DomainMetadata, DomainStatus

    class MyDomainAdapter(DomainAdapter):
        def get_metadata(self) -> DomainMetadata:
            return DomainMetadata(...)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Type


class DomainStatus(Enum):
    """Status of a domain plugin."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    UPDATING = "updating"
    ERROR = "error"


@dataclass
class DomainMetadata:
    """Metadata for a domain plugin."""

    name: str
    version: str
    description: str
    author: str
    status: DomainStatus = DomainStatus.INACTIVE
    config_schema: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class QueryResult:
    """Result of processing a query through a domain adapter."""

    response: str
    domain: str
    claims_extracted: List[Dict[str, Any]] = field(default_factory=list)
    gmif_classification: Optional[Dict[str, Any]] = None
    governance_passed: bool = True
    blocked_claims: List[Dict[str, Any]] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    escalation_triggered: bool = False
    escalation_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.5
    error: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of validating content against domain rules."""

    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class DomainAdapter(ABC):
    """
    Abstract base class for domain-specific adapters.

    All domain plugins must inherit from this class and implement
    the abstract methods to be compatible with the Grilo Falante
    platform.

    Example:
        from grilo_falante.platform.domain_adapter import DomainAdapter, DomainMetadata, DomainStatus

        class TaxIntelligenceAdapter(DomainAdapter):
            def get_metadata(self) -> DomainMetadata:
                return DomainMetadata(
                    name="tax_intelligence",
                    version="1.0.0",
                    description="Portuguese tax law domain adapter",
                    author="University of Porto",
                    status=DomainStatus.ACTIVE,
                )

            def get_routing_config(self) -> Dict[str, List[str]]:
                return {
                    "iva": ["IVA", "VAT", "fatura", "dedução"],
                    "irc": ["IRC", "corporate", "resultados", "lucros"],
                }

            def get_prompts(self) -> Dict[str, str]:
                return {
                    "system": "You are a Portuguese tax law expert...",
                    "query": "Analyse this tax question: {query}",
                }

            def get_escalation_triggers(self) -> List[str]:
                return ["reclamação", "inspeção", "multa", "urgente"]

            async def process_query(self, query: str, context: Dict, llm_config: Dict) -> QueryResult:
                # Implementation here
                pass

            async def validate_content(self, content: Any) -> ValidationResult:
                # Implementation here
                pass
    """

    @abstractmethod
    def get_metadata(self) -> DomainMetadata:
        """
        Return the metadata for this domain adapter.

        Returns:
            DomainMetadata with name, version, description, author, status
        """
        pass

    @abstractmethod
    def get_routing_config(self) -> Dict[str, List[str]]:
        """
        Return routing configuration for this domain.

        Returns:
            Dict mapping department/topic to list of keywords.
            Example:
                {
                    "academic": ["matrícula", "notas", "curso"],
                    "sasup": ["bolsa", "dormitório", "refeitório"],
                    "it": ["wifi", "password", "email"],
                }
        """
        pass

    @abstractmethod
    def get_prompts(self) -> Dict[str, str]:
        """
        Return prompt templates for this domain.

        Returns:
            Dict with prompt templates. Keys:
            - "system": System prompt for LLM
            - "query": Query processing prompt (with {query} placeholder)
            - "escalation": Escalation notification prompt
        """
        pass

    @abstractmethod
    def get_escalation_triggers(self) -> List[str]:
        """
        Return list of keywords that trigger human escalation.

        Returns:
            List of trigger words/phrases
        """
        pass

    @abstractmethod
    async def process_query(
        self,
        query: str,
        context: Dict[str, Any],
        llm_config: Dict[str, Any],
    ) -> QueryResult:
        """
        Process a user query through this domain adapter.

        Args:
            query: The user's query text
            context: Session context (user_id, conversation_history, etc.)
            llm_config: LLM configuration (endpoint, model, temperature)

        Returns:
            QueryResult with response and metadata
        """
        pass

    @abstractmethod
    async def validate_content(self, content: Any) -> ValidationResult:
        """
        Validate content against this domain's rules.

        Args:
            content: Content to validate (str, dict, or domain-specific type)

        Returns:
            ValidationResult with is_valid, errors, warnings
        """
        pass

    def get_department_for_query(self, query: str) -> Optional[str]:
        """
        Determine which department/topic this query belongs to.

        Default implementation uses keyword matching from routing_config.
        Can be overridden for more sophisticated routing.

        Args:
            query: The query text

        Returns:
            Department name or None if no match
        """
        query_lower = query.lower()
        routing_config = self.get_routing_config()

        for department, keywords in routing_config.items():
            for keyword in keywords:
                if keyword.lower() in query_lower:
                    return department

        return None

    def should_escalate(
        self, query: str, response: Optional[str] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Determine if this query/response should trigger escalation.

        Default implementation checks for escalation_trigger keywords in query.
        Can be overridden for more sophisticated logic.

        Args:
            query: The user's query
            response: Optional response text

        Returns:
            Tuple of (should_escalate, reason)
        """
        query_lower = query.lower()
        triggers = self.get_escalation_triggers()

        for trigger in triggers:
            if trigger.lower() in query_lower:
                return True, f"Trigger keyword found: '{trigger}'"

        return False, None

    def get_llm_config(self, provider: str = "bitnet") -> Dict[str, Any]:
        """
        Get LLM configuration for this domain.

        Can be overridden to provide domain-specific LLM settings.

        Args:
            provider: LLM provider name

        Returns:
            Dict with endpoint, model, temperature, etc.
        """
        from grilo_falante.config import get_llm_config as get_config

        return get_config(provider)
