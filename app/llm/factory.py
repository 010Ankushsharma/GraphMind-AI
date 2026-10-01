"""Factory for LLM providers with optional fallback."""
import logging

from app.config.settings import Settings
from app.llm.anthropic_provider import AnthropicProvider
from app.llm.base import BaseLLMProvider, LLMUnavailableError
from app.llm.gemini_provider import GeminiProvider
from app.llm.mock_provider import MockLLMProvider
from app.llm.ollama_provider import OllamaProvider
from app.llm.openai_compatible_provider import OpenAICompatibleProvider
from app.llm.openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)


class ResolvingLLMProvider(BaseLLMProvider):
    """Primary provider with optional fallback on unavailability."""

    def __init__(self, primary: BaseLLMProvider, fallback: BaseLLMProvider | None):
        self._primary = primary
        self._fallback = fallback
        self._last_used: BaseLLMProvider = primary

    @property
    def name(self) -> str:
        return self._last_used.name

    @property
    def configured_primary(self) -> str:
        return self._primary.name

    def generate_text(self, system_prompt: str, user_prompt: str, structured_schema=None):
        try:
            if isinstance(self._primary, OllamaProvider) and not self._primary.health_check():
                raise LLMUnavailableError("Ollama server is not reachable")
            self._last_used = self._primary
            return self._primary.generate_text(
                system_prompt, user_prompt, structured_schema
            )
        except LLMUnavailableError as exc:
            if self._fallback is None:
                raise
            logger.warning(
                "Primary LLM provider %s unavailable (%s); using fallback %s",
                self._primary.name,
                exc,
                self._fallback.name,
            )
            self._last_used = self._fallback
            return self._fallback.generate_text(
                system_prompt, user_prompt, structured_schema
            )


class LLMProviderFactory:
    @staticmethod
    def create(settings: Settings) -> BaseLLMProvider:
        provider_name = settings.llm_provider
        if provider_name == "auto":
            provider_name = "ollama"

        primary = _build_single(provider_name, settings)
        fallback = None
        if settings.llm_fallback_provider:
            try:
                fallback = _build_single(settings.llm_fallback_provider, settings)
            except LLMUnavailableError:
                logger.warning(
                    "Fallback provider %s could not be constructed",
                    settings.llm_fallback_provider,
                )

        if fallback and fallback.name != primary.name:
            return ResolvingLLMProvider(primary, fallback)
        return primary


def _build_single(name: str, settings: Settings) -> BaseLLMProvider:
    if name == "mock":
        return MockLLMProvider()
    if name == "ollama":
        return OllamaProvider(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            timeout_seconds=settings.ollama_timeout_seconds,
        )
    if name == "gemini":
        return GeminiProvider(
            api_key=settings.gemini_api_key,
            model=settings.gemini_model,
        )
    if name == "openai":
        return OpenAIProvider(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
        )
    if name == "anthropic":
        return AnthropicProvider(
            api_key=settings.anthropic_api_key,
            model=settings.anthropic_model,
        )
    if name == "openai_compatible":
        return OpenAICompatibleProvider(
            base_url=settings.openai_compatible_base_url,
            api_key=settings.openai_compatible_api_key,
            model=settings.openai_compatible_model,
        )
    raise LLMUnavailableError(f"Unsupported LLM_PROVIDER: {name}")
