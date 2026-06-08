"""
BitNet LLM Service - 1-bit LLM inference via bitnet.cpp

This module provides integration with BitNet models using the bitnet.cpp
inference framework from Microsoft.

BitNet uses 1.58-bit quantization (ternary: -1, 0, +1) for extreme
efficiency: 2-6x speedup and 55-82% energy reduction vs full-precision.
"""

import logging
from typing import AsyncIterator, Optional

import httpx

from grilo_falante.config import settings
from grilo_falante.backend.services.llm.base import (
    LLMService,
    LLMMessage,
    LLMResponse,
    LLMStreamChunk,
)

logger = logging.getLogger(__name__)


class BitNetService(LLMService):
    """
    BitNet LLM service via bitnet.cpp.

    bitnet.cpp is Microsoft's official inference framework for 1-bit LLMs.
    It provides a REST API similar to Ollama for compatibility.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
    ):
        self.base_url = base_url or settings.bitnet_base_url
        self.model = model or settings.bitnet_model
        self.temperature = temperature or settings.bitnet_temperature

    @property
    def name(self) -> str:
        return f"bitnet/{self.model}"

    @property
    def default_temperature(self) -> float:
        return self.temperature

    @property
    def available(self) -> bool:
        """Check if BitNet server is available."""
        try:
            import httpx
            response = httpx.get(f"{self.base_url}/health", timeout=2.0)
            return response.status_code == 200
        except Exception:
            return False

    async def chat(
        self,
        messages: list[LLMMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> LLMResponse:
        """
        Send a chat completion request to BitNet.

        BitNet doesn't have native chat API, so we format as a prompt.
        """
        temp = temperature or self.temperature

        # Format messages as a prompt (BitNet doesn't have native chat)
        prompt = self._format_messages(messages)

        async with httpx.AsyncClient(timeout=180.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/completion",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": temp,
                            "num_predict": max_tokens or 512,
                        },
                        **kwargs,
                    },
                )
                response.raise_for_status()
                data = response.json()

                return LLMResponse(
                    content=data.get("content", ""),
                    model=self.model,
                    usage={
                        "prompt_tokens": data.get("prompt_eval_count", 0),
                        "completion_tokens": data.get("eval_count", 0),
                        "total_tokens": data.get("prompt_eval_count", 0)
                        + data.get("eval_count", 0),
                    },
                    finish_reason="stop" if data.get("done", False) else None,
                )

            except httpx.ConnectError:
                logger.error(f"Cannot connect to BitNet at {self.base_url}")
                raise ConnectionError(
                    f"BitNet service not available at {self.base_url}. "
                    "Ensure bitnet.cpp server is running."
                )
            except httpx.HTTPStatusError as e:
                logger.error(f"BitNet HTTP error: {e.response.status_code}")
                raise

    async def stream(
        self,
        messages: list[LLMMessage],
        temperature: Optional[float] = None,
        **kwargs,
    ) -> AsyncIterator[LLMStreamChunk]:
        """Stream a completion response from BitNet."""
        temp = temperature or self.temperature
        prompt = self._format_messages(messages)

        async with httpx.AsyncClient(timeout=180.0) as client:
            try:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/completion",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": True,
                        "options": {
                            "temperature": temp,
                        },
                        **kwargs,
                    },
                ) as response:
                    response.raise_for_status()

                    async for line in response.aiter_lines():
                        if not line.strip():
                            continue

                        if line.startswith("data:"):
                            line = line[5:].strip()

                        if not line or line == "[DONE]":
                            break

                        try:
                            import json

                            data = json.loads(line)
                        except json.JSONDecodeError:
                            continue

                        content = data.get("content", "")
                        if content:
                            yield LLMStreamChunk(
                                content=content,
                                delta=content,
                                finish_reason="stop" if data.get("done") else None,
                            )

            except httpx.ConnectError:
                logger.error(f"Cannot connect to BitNet at {self.base_url}")
                raise ConnectionError(f"BitNet service not available at {self.base_url}")

    def _format_messages(self, messages: list[LLMMessage]) -> str:
        """
        Format messages into a prompt string.

        BitNet doesn't have native chat support, so we convert messages
        to a simple prompt format.
        """
        parts = []

        for msg in messages:
            role = msg.role.lower()
            content = msg.content.strip()

            if role == "system":
                parts.append(f"System: {content}")
            elif role == "user":
                parts.append(f"User: {content}")
            elif role == "assistant":
                parts.append(f"Assistant: {content}")
            else:
                parts.append(content)

        prompt = "\n\n".join(parts)
        prompt += "\n\nAssistant:"

        return prompt

    async def list_models(self) -> list[str]:
        """List available models on the BitNet server."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(f"{self.base_url}/models")
                response.raise_for_status()
                data = response.json()
                return [m.get("name", m.get("model")) for m in data.get("models", [])]
            except Exception as e:
                logger.warning(f"Failed to list BitNet models: {e}")
                return [self.model]

    async def health_check(self) -> bool:
        """Check if BitNet service is available."""
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
            except Exception:
                return False
