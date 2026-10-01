"""Anthropic Claude provider."""
from app.llm.base import BaseLLMProvider, LLMResponse, LLMUnavailableError


class AnthropicProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise LLMUnavailableError("ANTHROPIC_API_KEY is not configured")
        self._api_key = api_key
        self._model = model

    @property
    def name(self) -> str:
        return "anthropic"

    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        structured_schema: dict | None = None,
    ) -> LLMResponse:
        try:
            from anthropic import Anthropic
        except ImportError as exc:
            raise LLMUnavailableError("anthropic package is not installed") from exc

        client = Anthropic(api_key=self._api_key)
        try:
            message = client.messages.create(
                model=self._model,
                max_tokens=2048,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
        except Exception as exc:
            msg = str(exc)
            if "401" in msg or "authentication" in msg.lower():
                raise LLMUnavailableError("Anthropic authentication failed") from exc
            raise LLMUnavailableError(f"Anthropic error: {msg[:200]}") from exc

        parts = []
        for block in message.content:
            if getattr(block, "type", None) == "text":
                parts.append(block.text)
        text = "".join(parts)
        if not text.strip():
            raise LLMUnavailableError("Anthropic returned empty response")
        return LLMResponse(text=text.strip(), provider_name=self.name)
