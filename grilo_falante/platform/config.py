"""
Platform Configuration - LLM and infrastructure settings.

Provides centralized LLM configuration for the Grilo Falante platform
with BitNet as the default provider.

Usage:
    from grilo_falante.platform.config import (
        get_llm_config,
        get_llm_provider,
        set_default_provider,
    )

    # Get LLM config for a specific provider
    config = get_llm_config("bitnet")

    # Get config for default provider
    config = get_llm_config()

    # Check if provider is available
    if is_provider_available("ollama"):
        ...
"""

import os
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from typing import Any, Dict, Optional

from grilo_falante.config import Settings, get_settings


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    BITNET = "bitnet"
    OLLAMA = "ollama"
    OPENAI = "openai"
    IAEDU = "iaedu"
    OPENWEBUI = "openwebui"
    ANTHROPIC = "anthropic"


@dataclass
class LLMConfig:
    """Configuration for an LLM provider."""
    provider: str
    endpoint: str
    model: str
    temperature: float = 0.3
    max_tokens: int = 4096
    timeout: int = 120
    extra: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "endpoint": self.endpoint,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout,
            **(self.extra or {}),
        }


BITNET_DEFAULT_CONFIG = LLMConfig(
    provider="bitnet",
    endpoint="http://localhost:8002/completion",
    model="microsoft/bitnet-bge-m3",
    temperature=0.3,
    max_tokens=2048,
    timeout=120,
)

OLLAMA_DEFAULT_CONFIG = LLMConfig(
    provider="ollama",
    endpoint="http://localhost:11434/api/generate",
    model="llama3.2",
    temperature=0.3,
    max_tokens=4096,
    timeout=120,
)

OPENAI_DEFAULT_CONFIG = LLMConfig(
    provider="openai",
    endpoint="https://api.openai.com/v1/completions",
    model="gpt-4o",
    temperature=0.3,
    max_tokens=4096,
    timeout=120,
)

IAEDU_DEFAULT_CONFIG = LLMConfig(
    provider="iaedu",
    endpoint="https://api.iaedu.pt/agent-chat/api/v1/agent/cmamvd3n40000c801qeacoad2/stream",
    model="gpt-4",
    temperature=0.3,
    max_tokens=4096,
    timeout=120,
)

PROVIDER_CONFIGS = {
    LLMProvider.BITNET: BITNET_DEFAULT_CONFIG,
    LLMProvider.OLLAMA: OLLAMA_DEFAULT_CONFIG,
    LLMProvider.OPENAI: OPENAI_DEFAULT_CONFIG,
    LLMProvider.IAEDU: IAEDU_DEFAULT_CONFIG,
}

DEFAULT_PROVIDER = LLMProvider.BITNET


def get_default_provider() -> LLMProvider:
    """
    Get the default LLM provider from environment or config.

    Returns:
        LLMProvider enum value
    """
    env_provider = os.getenv("GRILO_LLM_PROVIDER", "").lower()

    if env_provider:
        for provider in LLMProvider:
            if provider.value == env_provider:
                return provider

    try:
        settings = get_settings()
        if hasattr(settings, "llm_provider"):
            provider_str = str(settings.llm_provider.value).lower()
            for provider in LLMProvider:
                if provider.value == provider_str:
                    return provider
    except Exception:
        pass

    return DEFAULT_PROVIDER


def set_default_provider(provider: LLMProvider) -> None:
    """
    Set the default LLM provider.

    Args:
        provider: The LLMProvider to use as default
    """
    global DEFAULT_PROVIDER
    DEFAULT_PROVIDER = provider
    os.environ["GRILO_LLM_PROVIDER"] = provider.value


def get_llm_config(provider: Optional[str] = None) -> LLMConfig:
    """
    Get LLM configuration for a specific provider.

    Merges environment variables and settings with defaults.

    Args:
        provider: Provider name (bitnet, ollama, openai, iaedu).
                 If None, uses the default provider.

    Returns:
        LLMConfig with endpoint, model, temperature, etc.
    """
    if provider is None:
        provider = get_default_provider().value

    provider_enum = None
    for p in LLMProvider:
        if p.value == provider.lower():
            provider_enum = p
            break

    if provider_enum is None:
        provider_enum = DEFAULT_PROVIDER

    base_config = PROVIDER_CONFIGS.get(provider_enum, BITNET_DEFAULT_CONFIG)

    settings = get_settings()

    if provider_enum == LLMProvider.BITNET:
        return LLMConfig(
            provider="bitnet",
            endpoint=os.getenv(
                "BITNET_BASE_URL",
                getattr(settings, "bitnet_base_url", "http://localhost:8002"),
            ),
            model=os.getenv(
                "BITNET_MODEL",
                getattr(settings, "bitnet_model", "microsoft/bitnet-bge-m3"),
            ),
            temperature=float(os.getenv(
                "BITNET_TEMPERATURE",
                getattr(settings, "bitnet_temperature", 0.3),
            )),
        )

    elif provider_enum == LLMProvider.OLLAMA:
        return LLMConfig(
            provider="ollama",
            endpoint=os.getenv(
                "OLLAMA_BASE_URL",
                getattr(settings, "ollama_base_url", "http://localhost:11434"),
            ),
            model=os.getenv(
                "OLLAMA_MODEL",
                getattr(settings, "ollama_model", "llama3.2"),
            ),
            temperature=float(os.getenv(
                "OLLAMA_TEMPERATURE",
                getattr(settings, "ollama_temperature", 0.3),
            )),
        )

    elif provider_enum == LLMProvider.OPENAI:
        return LLMConfig(
            provider="openai",
            endpoint="https://api.openai.com/v1/completions",
            model=os.getenv(
                "OPENAI_MODEL",
                getattr(settings, "openai_model", "gpt-4o"),
            ),
            temperature=float(os.getenv(
                "OPENAI_TEMPERATURE",
                getattr(settings, "openai_temperature", 0.3),
            )),
            extra={"api_key": os.getenv("OPENAI_API_KEY", settings.openai_api_key or "")},
        )

    elif provider_enum == LLMProvider.IAEDU:
        return LLMConfig(
            provider="iaedu",
            endpoint=os.getenv(
                "IAEDU_ENDPOINT",
                getattr(settings, "iaedu_endpoint", "https://api.iaedu.pt/agent-chat/api/v1/agent/cmamvd3n40000c801qeacoad2/stream"),
            ),
            model="gpt-4",
            extra={"api_key": os.getenv("IAEDU_API_KEY", settings.iaedu_api_key or "")},
        )

    return base_config


def is_provider_available(provider: str) -> bool:
    """
    Check if an LLM provider is available/configured.

    Args:
        provider: Provider name

    Returns:
        True if provider is available
    """
    try:
        config = get_llm_config(provider)

        if provider == LLMProvider.BITNET.value:
            return True

        elif provider == LLMProvider.OLLAMA.value:
            return True

        elif provider == LLMProvider.OPENAI.value:
            return bool(os.getenv("OPENAI_API_KEY"))

        elif provider == LLMProvider.IAEDU.value:
            return bool(os.getenv("IAEDU_API_KEY"))

        return False

    except Exception:
        return False


def list_available_providers() -> list[str]:
    """
    List all available LLM providers.

    Returns:
        List of provider names
    """
    available = []
    for provider in LLMProvider:
        if is_provider_available(provider.value):
            available.append(provider.value)
    return available


class LLMClient:
    """
    Generic LLM client that can use any configured provider.

    Usage:
        client = LLMClient()  # Uses default provider
        response = await client.generate("Hello, world!")

        client = LLMClient(provider="ollama")
        response = await client.generate("Hello!")
    """

    def __init__(self, provider: Optional[str] = None):
        """
        Initialize LLM client.

        Args:
            provider: Specific provider to use, or None for default
        """
        self.provider_name = provider
        self.config = get_llm_config(provider)

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Generate text using the configured LLM.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            **kwargs: Additional provider-specific arguments

        Returns:
            Generated text
        """
        if self.config.provider == LLMProvider.BITNET.value:
            return await self._generate_bitnet(prompt, system_prompt, **kwargs)
        elif self.config.provider == LLMProvider.OLLAMA.value:
            return await self._generate_ollama(prompt, system_prompt, **kwargs)
        elif self.config.provider == LLMProvider.OPENAI.value:
            return await self._generate_openai(prompt, system_prompt, **kwargs)
        else:
            raise NotImplementedError(f"Provider {self.config.provider} not implemented")

    async def _generate_bitnet(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> str:
        """Generate using BitNet."""
        import httpx

        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            response = await client.post(
                self.config.endpoint,
                json={
                    "prompt": full_prompt,
                    "temperature": kwargs.get("temperature", self.config.temperature),
                    "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                },
            )
            response.raise_for_status()
            return response.json().get("content", "")

    async def _generate_ollama(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> str:
        """Generate using Ollama."""
        import httpx

        payload = {
            "prompt": prompt,
            "model": self.config.model,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "options": {"num_ctx": kwargs.get("num_ctx", 4096)},
        }

        if system_prompt:
            payload["system"] = system_prompt

        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            response = await client.post(
                f"{self.config.endpoint}",
                json=payload,
            )
            response.raise_for_status()
            return response.json().get("response", "")

    async def _generate_openai(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> str:
        """Generate using OpenAI."""
        import httpx

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {self.config.extra.get('api_key', '')}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            response = await client.post(
                self.config.endpoint,
                headers=headers,
                json={
                    "model": self.config.model,
                    "messages": messages,
                    "temperature": kwargs.get("temperature", self.config.temperature),
                },
            )
            response.raise_for_status()
            data = response.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "")


@dataclass
class PlatformConfig:
    """Main platform configuration."""
    default_llm_provider: LLMProvider = DEFAULT_PROVIDER
    database_url: str = "postgresql://postgres:postgres@localhost:5432/grilo_falante"
    lake_path: str = "./lake"
    log_level: str = "info"
    debug: bool = False

    @classmethod
    def from_env(cls) -> "PlatformConfig":
        """Load config from environment variables."""
        return cls(
            default_llm_provider=get_default_provider(),
            database_url=os.getenv("DATABASE_URL", cls.database_url),
            lake_path=os.getenv("LAKE_PATH", cls.lake_path),
            log_level=os.getenv("LOG_LEVEL", cls.log_level),
            debug=os.getenv("DEBUG", "").lower() in ("1", "true", "yes"),
        )


@lru_cache
def get_platform_config() -> PlatformConfig:
    """Get cached platform configuration."""
    return PlatformConfig.from_env()
