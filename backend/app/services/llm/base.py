"""LLM provider interface."""

from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    """Abstract interface for chat and embedding providers."""

    @abstractmethod
    def generate_response(self, prompt: str, **kwargs: Any) -> str:
        """Generate a chat completion from a prompt."""
        ...

    @abstractmethod
    def embed(self, texts: list[str], **kwargs: Any) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        ...
