"""Ollama local LLM provider."""
import logging

import httpx

from app.llm.base import BaseLLMProvider, LLMResponse, LLMUnavailableError

logger = logging.getLogger(__name__)


class OllamaProvider(BaseLLMProvider):
    def __init__(
        self,
        base_url: str,
        model: str,
        timeout_seconds: int = 120,
    ):
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout = timeout_seconds

    @property
    def name(self) -> str:
        return "ollama"

    def health_check(self) -> bool:
        try:
            with httpx.Client(timeout=5.0) as client:
                r = client.get(f"{self._base_url}/api/tags")
                return r.status_code == 200
        except httpx.HTTPError:
            return False

    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        structured_schema: dict | None = None,
    ) -> LLMResponse:
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
        }
        if structured_schema:
            payload["format"] = "json"

        try:
            with httpx.Client(timeout=float(self._timeout)) as client:
                response = client.post(
                    f"{self._base_url}/api/chat",
                    json=payload,
                )
        except httpx.TimeoutException as exc:
            raise LLMUnavailableError("Ollama request timed out") from exc
        except httpx.HTTPError as exc:
            raise LLMUnavailableError(f"Ollama unavailable: {exc}") from exc

        if response.status_code == 404:
            raise LLMUnavailableError(
                f"Ollama model not found: {self._model}"
            )
        if response.status_code >= 400:
            raise LLMUnavailableError(
                f"Ollama error ({response.status_code}): {response.text[:200]}"
            )

        data = response.json()
        message = data.get("message", {})
        content = message.get("content", "")
        if not content:
            raise LLMUnavailableError("Ollama returned empty response")
        return LLMResponse(text=content.strip(), provider_name=self.name)
