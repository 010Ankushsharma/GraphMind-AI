from unittest.mock import MagicMock, patch

import pytest

from app.config.settings import Settings
from app.llm.anthropic_provider import AnthropicProvider
from app.llm.factory import LLMProviderFactory
from app.llm.gemini_provider import GeminiProvider
from app.llm.mock_provider import MockLLMProvider
from app.llm.ollama_provider import OllamaProvider
from app.llm.openai_compatible_provider import OpenAICompatibleProvider
from app.llm.openai_provider import OpenAIProvider


def _settings(**overrides):
    base = {
        "LLM_PROVIDER": "mock",
        "OLLAMA_BASE_URL": "http://localhost:11434",
        "OLLAMA_MODEL": "llama3.2",
        "GEMINI_API_KEY": "test-key",
        "GEMINI_MODEL": "gemini-2.5-flash-lite",
        "OPENAI_API_KEY": "test-key",
        "OPENAI_MODEL": "gpt-4o-mini",
        "ANTHROPIC_API_KEY": "test-key",
        "ANTHROPIC_MODEL": "claude-3-5-haiku-latest",
        "OPENAI_COMPATIBLE_BASE_URL": "http://localhost:9999/v1",
        "OPENAI_COMPATIBLE_API_KEY": "k",
        "OPENAI_COMPATIBLE_MODEL": "local-model",
    }
    base.update(overrides)
    return Settings(**base)


def test_factory_mock():
    provider = LLMProviderFactory.create(_settings(LLM_PROVIDER="mock"))
    assert isinstance(provider, MockLLMProvider)


def test_factory_ollama():
    provider = LLMProviderFactory.create(_settings(LLM_PROVIDER="ollama"))
    assert isinstance(provider, OllamaProvider)


def test_factory_gemini():
    provider = LLMProviderFactory.create(_settings(LLM_PROVIDER="gemini"))
    assert isinstance(provider, GeminiProvider)


def test_factory_openai():
    provider = LLMProviderFactory.create(_settings(LLM_PROVIDER="openai"))
    assert isinstance(provider, OpenAIProvider)


def test_factory_anthropic():
    provider = LLMProviderFactory.create(_settings(LLM_PROVIDER="anthropic"))
    assert isinstance(provider, AnthropicProvider)


def test_factory_openai_compatible():
    provider = LLMProviderFactory.create(_settings(LLM_PROVIDER="openai_compatible"))
    assert isinstance(provider, OpenAICompatibleProvider)


@patch("app.llm.ollama_provider.httpx.Client")
def test_ollama_generate(mock_client_cls):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "message": {"content": '{"operation":"count"}'}
    }
    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.post.return_value = mock_response
    mock_client.get.return_value = mock_response
    mock_client_cls.return_value = mock_client

    provider = OllamaProvider("http://localhost:11434", "llama3.2", 30)
    out = provider.generate_text("sys", "user")
    assert out.provider_name == "ollama"
