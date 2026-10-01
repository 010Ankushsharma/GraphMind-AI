"""Abstract LLM provider interface."""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMResponse:
    text: str
    provider_name: str


class LLMProviderError(Exception):
    """Base error for LLM provider failures."""


class LLMUnavailableError(LLMProviderError):
    """Provider is not reachable or not configured."""


class BaseLLMProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        structured_schema: dict | None = None,
    ) -> LLMResponse:
        ...

    def health_check(self) -> bool:
        """Optional lightweight availability check."""
        return True
