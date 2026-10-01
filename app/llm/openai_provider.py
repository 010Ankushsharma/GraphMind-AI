"""OpenAI API provider."""
from app.llm.base import BaseLLMProvider, LLMResponse, LLMUnavailableError


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise LLMUnavailableError("OPENAI_API_KEY is not configured")
        self._api_key = api_key
        self._model = model

    @property
    def name(self) -> str:
        return "openai"

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

        client = OpenAI(api_key=self._api_key)
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
            msg = str(exc)
            if "401" in msg or "authentication" in msg.lower():
                raise LLMUnavailableError("OpenAI authentication failed") from exc
            raise LLMUnavailableError(f"OpenAI error: {msg[:200]}") from exc

        content = completion.choices[0].message.content or ""
        if not content.strip():
            raise LLMUnavailableError("OpenAI returned empty response")
        return LLMResponse(text=content.strip(), provider_name=self.name)
