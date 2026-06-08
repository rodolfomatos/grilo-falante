"""
Grilo Falante v3.0 — Centralized Configuration

Loads settings from environment variables with validation.
"""

import os
from enum import Enum
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProvider(str, Enum):
    OLLAMA = "ollama"
    OPENAI = "openai"
    IAEDU = "iaedu"
    OPENWEBUI = "openwebui"
    ANTHROPIC = "anthropic"
    BITNET = "bitnet"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/grilo_falante"
    postgres_password: str = "postgres"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_token: Optional[str] = None
    api_rate_limit: int = 60

    # Logging
    log_level: str = "info"

    # LLM Provider
    llm_provider: LLMProvider = LLMProvider.BITNET

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    ollama_temperature: float = 0.3
    ollama_num_ctx: int = 4096

    # OpenAI
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o"
    openai_temperature: float = 0.3

    # Anthropic
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-5-sonnet"

    # IAEDU (University of Porto academic API)
    iaedu_api_key: Optional[str] = None
    iaedu_endpoint: str = (
        "https://api.iaedu.pt/agent-chat/api/v1/agent/cmamvd3n40000c801qeacoad2/stream"
    )
    iaedu_channel_id: str = "cmh0rfgmn0i64j801uuoletwy"

    # OpenWebUI
    openwebui_base_url: str = "http://localhost:8080"
    openwebui_api_key: Optional[str] = None

    # BitNet (1-bit LLM via bitnet.cpp)
    bitnet_base_url: str = "http://localhost:8002"
    bitnet_model: str = "BitNet-b1.58-2B-4T"
    bitnet_temperature: float = 0.3

    # MCP
    mcp_transport: str = "stdio"

    # OpenDataLoader PDF (local mode only)
    opendataloader_java_path: Optional[str] = None
    opendataloader_mode: str = "local"

    # Paths
    lake_path: str = "./lake"

    # Evidence thresholds
    evidence_threshold: float = 0.5
    m4_block_threshold: float = 0.4

    # Curator scoring
    curator_reward: float = 0.05
    curator_penalty: float = 0.1
    curator_suspension_threshold: float = 0.3

    # Graph lint
    lint_enabled: bool = True

    @property
    def requires_api_token(self) -> bool:
        return bool(self.api_token)

    @property
    def ollama_available(self) -> bool:
        return self.llm_provider == LLMProvider.OLLAMA

    @property
    def iaedu_available(self) -> bool:
        return bool(self.iaedu_api_key and self.llm_provider == LLMProvider.IAEDU)

    @property
    def openwebui_available(self) -> bool:
        return bool(self.openwebui_api_key and self.llm_provider == LLMProvider.OPENWEBUI)

    @property
    def bitnet_available(self) -> bool:
        return self.llm_provider == LLMProvider.BITNET


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
