"""
LLM Service Abstraction Layer

Provides a unified interface for multiple LLM backends:
- Ollama (local)
- IAEDU (University of Porto academic API)
- OpenWebUI
- OpenAI (GPT-4o)
- Anthropic (Claude)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import AsyncIterator, Optional

import httpx

from grilo_falante.config import settings


@dataclass
class LLMMessage:
    role: str
    content: str


@dataclass
class LLMResponse:
    content: str
    model: str
    usage: dict = field(default_factory=dict)
    finish_reason: Optional[str] = None


@dataclass
class LLMStreamChunk:
    content: str
    delta: Optional[str] = None
    finish_reason: Optional[str] = None


class LLMService(ABC):
    """Abstract base class for LLM services."""

    @abstractmethod
    async def chat(
        self,
        messages: list[LLMMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> LLMResponse:
        """Send a chat completion request."""
        pass

    @abstractmethod
    async def stream(
        self,
        messages: list[LLMMessage],
        temperature: Optional[float] = None,
        **kwargs,
    ) -> AsyncIterator[LLMStreamChunk]:
        """Stream a chat completion response."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the service name."""
        pass

    @property
    def default_temperature(self) -> float:
        return 0.3


class OllamaService(LLMService):
    """Ollama local LLM service."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.base_url = base_url or settings.ollama_base_url
        self.model = model or settings.ollama_model
        self.temperature = settings.ollama_temperature
        self.num_ctx = settings.ollama_num_ctx

    @property
    def name(self) -> str:
        return f"ollama/{self.model}"

    @property
    def default_temperature(self) -> float:
        return self.temperature

    async def chat(
        self,
        messages: list[LLMMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> LLMResponse:
        temp = temperature or self.temperature

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": [{"role": m.role, "content": m.content} for m in messages],
                    "temperature": temp,
                    "num_ctx": self.num_ctx,
                    **kwargs,
                },
            )
            response.raise_for_status()
            data = response.json()

            return LLMResponse(
                content=data["message"]["content"],
                model=self.model,
                usage=data.get("usage", {}),
                finish_reason=data.get("done_reason"),
            )

    async def stream(
        self,
        messages: list[LLMMessage],
        temperature: Optional[float] = None,
        **kwargs,
    ) -> AsyncIterator[LLMStreamChunk]:
        temp = temperature or self.temperature

        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": [{"role": m.role, "content": m.content} for m in messages],
                    "temperature": temp,
                    "stream": True,
                    **kwargs,
                },
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        import json

                        data = json.loads(line)
                        if "message" in data:
                            yield LLMStreamChunk(
                                content=data["message"]["content"],
                                delta=data["message"].get("content"),
                                finish_reason=data.get("done_reason"),
                            )


class IAEDUService(LLMService):
    """
    IAEDU adapter service for University of Porto academic API.

    This wraps the iaedu-adapter which translates OpenAI-format requests
    to the iaedu.pt proprietary API format.
    """

    def __init__(
        self,
        endpoint: Optional[str] = None,
        channel_id: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        self.endpoint = endpoint or settings.iaedu_endpoint
        self.channel_id = channel_id or settings.iaedu_channel_id
        self.api_key = api_key or settings.iaedu_api_key
        self.base_url = "http://localhost:4000"

    @property
    def name(self) -> str:
        return "iaedu/chat"

    async def chat(
        self,
        messages: list[LLMMessage],
        temperature: Optional[float] = None,
        **kwargs,
    ) -> LLMResponse:
        import uuid

        thread_id = f"req-{uuid.uuid4()}"

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "messages": [{"role": m.role, "content": m.content} for m in messages],
                    "chat_id": thread_id,
                    "temperature": temperature or 0.3,
                },
                headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {},
            )
            response.raise_for_status()

            content = response.text
            return LLMResponse(
                content=content,
                model="iaedu-custom",
                usage={},
            )

    async def stream(
        self,
        messages: list[LLMMessage],
        temperature: Optional[float] = None,
        **kwargs,
    ) -> AsyncIterator[LLMStreamChunk]:
        import uuid

        thread_id = f"req-{uuid.uuid4()}"
        full_content = ""

        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/v1/chat/completions",
                json={
                    "messages": [{"role": m.role, "content": m.content} for m in messages],
                    "chat_id": thread_id,
                    "temperature": temperature or 0.3,
                    "stream": True,
                },
                headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {},
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        import json

                        data = json.loads(line[6:])
                        if data.get("choices"):
                            delta = data["choices"][0].get("delta", {}).get("content", "")
                            if delta:
                                full_content += delta
                                yield LLMStreamChunk(content=delta, delta=delta)


class OpenWebUIService(LLMService):
    """OpenWebUI bridge service."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        self.base_url = base_url or settings.openwebui_base_url
        self.api_key = api_key or settings.openwebui_api_key or "dummy"

    @property
    def name(self) -> str:
        return "openwebui"

    async def chat(
        self,
        messages: list[LLMMessage],
        temperature: Optional[float] = None,
        **kwargs,
    ) -> LLMResponse:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "model": "local-model",
                    "messages": [{"role": m.role, "content": m.content} for m in messages],
                    "temperature": temperature or 0.3,
                },
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "HTTP-Referer": self.base_url,
                },
            )
            response.raise_for_status()
            data = response.json()

            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                model=data.get("model", "openwebui"),
                usage=data.get("usage", {}),
            )

    async def stream(
        self,
        messages: list[LLMMessage],
        temperature: Optional[float] = None,
        **kwargs,
    ) -> AsyncIterator[LLMStreamChunk]:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/v1/chat/completions",
                json={
                    "model": "local-model",
                    "messages": [{"role": m.role, "content": m.content} for m in messages],
                    "temperature": temperature or 0.3,
                    "stream": True,
                },
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "HTTP-Referer": self.base_url,
                },
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        import json

                        data = json.loads(line[6:])
                        if data.get("choices"):
                            delta = data["choices"][0].get("delta", {}).get("content", "")
                            if delta:
                                yield LLMStreamChunk(content=delta, delta=delta)


class OpenAIService(LLMService):
    """OpenAI GPT-4o service."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.openai_model

    @property
    def name(self) -> str:
        return f"openai/{self.model}"

    async def chat(
        self,
        messages: list[LLMMessage],
        temperature: Optional[float] = None,
        **kwargs,
    ) -> LLMResponse:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": [{"role": m.role, "content": m.content} for m in messages],
                    "temperature": temperature or 0.3,
                },
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()
            data = response.json()

            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                model=self.model,
                usage=data.get("usage", {}),
                finish_reason=data["choices"][0].get("finish_reason"),
            )

    async def stream(
        self,
        messages: list[LLMMessage],
        temperature: Optional[float] = None,
        **kwargs,
    ) -> AsyncIterator[LLMStreamChunk]:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                "https://api.openai.com/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": [{"role": m.role, "content": m.content} for m in messages],
                    "temperature": temperature or 0.3,
                    "stream": True,
                },
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        import json

                        data = json.loads(line[6:])
                        if data.get("choices"):
                            delta = data["choices"][0].get("delta", {}).get("content", "")
                            if delta:
                                yield LLMStreamChunk(content=delta, delta=delta)


class LLMServiceFactory:
    """Factory for creating LLM service instances."""

    _instances: dict[str, LLMService] = {}

    @classmethod
    def get_service(cls, provider: Optional[str] = None) -> LLMService:
        provider = provider or settings.llm_provider.value

        if provider in cls._instances:
            return cls._instances[provider]

        if provider == "ollama":
            service = OllamaService()
        elif provider == "iaedu":
            service = IAEDUService()
        elif provider == "openwebui":
            service = OpenWebUIService()
        elif provider == "openai":
            service = OpenAIService()
        elif provider == "bitnet":
            from grilo_falante.backend.services.llm.bitnet import BitNetService

            service = BitNetService()
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")

        cls._instances[provider] = service
        return service

    @classmethod
    def clear(cls):
        cls._instances.clear()


def get_llm_service(provider: Optional[str] = None) -> LLMService:
    return LLMServiceFactory.get_service(provider)
