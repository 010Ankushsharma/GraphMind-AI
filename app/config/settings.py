"""Application configuration via Pydantic Settings."""
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

LLMProviderName = Literal[
    "ollama",
    "gemini",
    "openai",
    "anthropic",
    "openai_compatible",
    "mock",
    "auto",
]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="Ecommerce Knowledge Graph AI", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    llm_provider: LLMProviderName = Field(default="mock", alias="LLM_PROVIDER")
    llm_fallback_provider: LLMProviderName | None = Field(
        default=None, alias="LLM_FALLBACK_PROVIDER"
    )

    ollama_base_url: str = Field(
        default="http://localhost:11434", alias="OLLAMA_BASE_URL"
    )
    ollama_model: str = Field(default="llama3.2", alias="OLLAMA_MODEL")
    ollama_timeout_seconds: int = Field(default=120, alias="OLLAMA_TIMEOUT_SECONDS")

    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-2.5-flash-lite", alias="GEMINI_MODEL")

    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")

    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(
        default="claude-3-5-haiku-latest", alias="ANTHROPIC_MODEL"
    )

    openai_compatible_base_url: str = Field(
        default="", alias="OPENAI_COMPATIBLE_BASE_URL"
    )
    openai_compatible_api_key: str = Field(
        default="", alias="OPENAI_COMPATIBLE_API_KEY"
    )
    openai_compatible_model: str = Field(
        default="", alias="OPENAI_COMPATIBLE_MODEL"
    )

    max_graph_hops: int = Field(default=4, alias="MAX_GRAPH_HOPS")
    max_query_results: int = Field(default=50, alias="MAX_QUERY_RESULTS")

    data_dir: str = Field(default="data", alias="DATA_DIR")

    @property
    def data_path(self) -> Path:
        root = Path(__file__).resolve().parents[2]
        return root / self.data_dir


@lru_cache
def get_settings() -> Settings:
    return Settings()
