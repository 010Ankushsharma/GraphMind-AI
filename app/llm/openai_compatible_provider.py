"""OpenAI-compatible HTTP API provider."""
from app.llm.base import BaseLLMProvider, LLMResponse, LLMUnavailableError


class OpenAICompatibleProvider(BaseLLMProvider):
    def __init__(self, base_url: str, api_key: str, model: str):
        if not base_url or not model:
            raise LLMUnavailableError(
                "OPENAI_COMPATIBLE_BASE_URL and OPENAI_COMPATIBLE_MODEL are required"
            )
        self._base_url = base_url
        self._api_key = api_key
        self._model = model

    @property
    def name(self) -> str:
        return "openai_compatible"

    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        structured_schema: dict | None = None,
    ) -> LLMResponse:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise LLMUnavailableError("openai package is not installed") from exc

        client = OpenAI(base_url=self._base_url, api_key=self._api_key or "not-needed")
        kwargs: dict = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        if structured_schema:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            completion = client.chat.completions.create(**kwargs)
        except Exception as exc:
            raise LLMUnavailableError(
                f"OpenAI-compatible API error: {str(exc)[:200]}"
            ) from exc

        content = completion.choices[0].message.content or ""
        if not content.strip():
            raise LLMUnavailableError("OpenAI-compatible API returned empty response")
        return LLMResponse(text=content.strip(), provider_name=self.name)
