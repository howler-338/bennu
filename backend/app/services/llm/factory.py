"""LLM provider factory."""

import os

from app.services.llm.base import LLMProvider
from app.services.llm.ollama import OllamaProvider


def get_llm_provider(provider: str | None = None) -> LLMProvider:
    """Return the configured LLM provider implementation."""
    name = provider or os.getenv("LLM_PROVIDER", "ollama")

    if name == "ollama":
        return OllamaProvider(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            chat_model=os.getenv("OLLAMA_CHAT_MODEL", "llama3"),
            embed_model=os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text"),
        )

    raise ValueError(f"Unknown LLM provider: {name}")
