"""Google Gemini provider using google-genai SDK."""
import logging

from app.llm.base import BaseLLMProvider, LLMResponse, LLMUnavailableError

logger = logging.getLogger(__name__)


class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise LLMUnavailableError("GEMINI_API_KEY is not configured")
        self._api_key = api_key
        self._model = model
        self._client = None

    @property
    def name(self) -> str:
        return "gemini"

    def _get_client(self):
        if self._client is None:
            try:
                from google import genai
            except ImportError as exc:
                raise LLMUnavailableError(
                    "google-genai package is not installed"
                ) from exc
            self._client = genai.Client(api_key=self._api_key)
        return self._client

    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        structured_schema: dict | None = None,
    ) -> LLMResponse:
        client = self._get_client()
        prompt = f"{system_prompt}\n\n{user_prompt}"
        config = None
        if structured_schema:
            try:
                from google.genai import types

                config = types.GenerateContentConfig(
                    response_mime_type="application/json",
                )
            except Exception:
                config = None

        try:
            response = client.models.generate_content(
                model=self._model,
                contents=prompt,
                config=config,
            )
        except Exception as exc:
            msg = str(exc)
            if "429" in msg or "quota" in msg.lower():
                raise LLMUnavailableError("Gemini quota or rate limit exceeded") from exc
            if "401" in msg or "403" in msg or "API key" in msg:
                raise LLMUnavailableError("Gemini authentication failed") from exc
            raise LLMUnavailableError(f"Gemini error: {msg[:200]}") from exc

        text = getattr(response, "text", None) or ""
        if not text.strip():
            raise LLMUnavailableError("Gemini returned empty response")
        return LLMResponse(text=text.strip(), provider_name=self.name)
