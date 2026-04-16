"""
Grilo Falante Platform - Domain adapter SDK and plugin management.

This module provides the platform infrastructure for building domain-specific
adapters that integrate with the Grilo Falante epistemic governance regime.

Usage:
    from grilo_falante.platform import DomainAdapter, PluginRegistry, get_llm_config

    # Define a domain adapter
    class MyDomain(DomainAdapter):
        ...

    # Register it
    PluginRegistry.register("my_domain", MyDomain)

    # Use it
    adapter = PluginRegistry.get("my_domain")
"""

from grilo_falante.platform.domain_adapter import (
    DomainAdapter,
    DomainMetadata,
    DomainStatus,
    QueryResult,
    ValidationResult,
)

from grilo_falante.platform.registry import (
    PluginRegistry,
    PluginNotFoundError,
    PluginRegistrationError,
)

from grilo_falante.platform.config import (
    LLMProvider,
    LLMConfig,
    LLMClient,
    PlatformConfig,
    get_llm_config,
    get_default_provider,
    set_default_provider,
    is_provider_available,
    list_available_providers,
    get_platform_config,
)

__all__ = [
    # Domain adapter
    "DomainAdapter",
    "DomainMetadata",
    "DomainStatus",
    "QueryResult",
    "ValidationResult",
    # Registry
    "PluginRegistry",
    "PluginNotFoundError",
    "PluginRegistrationError",
    # Config
    "LLMProvider",
    "LLMConfig",
    "LLMClient",
    "PlatformConfig",
    "get_llm_config",
    "get_default_provider",
    "set_default_provider",
    "is_provider_available",
    "list_available_providers",
    "get_platform_config",
]
