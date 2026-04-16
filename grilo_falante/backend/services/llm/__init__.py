"""
LLM Service — Unified interface for multiple LLM backends.
"""

from grilo_falante.backend.services.llm.base import (
    LLMMessage,
    LLMResponse,
    LLMService,
    LLMStreamChunk,
    OllamaService,
    IAEDUService,
    OpenWebUIService,
    OpenAIService,
    LLMServiceFactory,
    get_llm_service,
)
from grilo_falante.backend.services.llm.bitnet import BitNetService

__all__ = [
    "LLMMessage",
    "LLMResponse",
    "LLMService",
    "LLMStreamChunk",
    "OllamaService",
    "IAEDUService",
    "OpenWebUIService",
    "OpenAIService",
    "BitNetService",
    "LLMServiceFactory",
    "get_llm_service",
]
