"""Ollama local inference provider."""

from typing import Any

import httpx

from app.services.llm.base import LLMProvider


class OllamaProvider(LLMProvider):
    """Local inference via Ollama HTTP API."""

    def __init__(
        self,
        base_url: str,
        chat_model: str,
        embed_model: str,
        timeout: float = 120.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.chat_model = chat_model
        self.embed_model = embed_model
        self.timeout = timeout

    def generate_response(self, prompt: str, **kwargs: Any) -> str:
        payload = {
            "model": kwargs.get("model", self.chat_model),
            "prompt": prompt,
            "stream": False,
        }
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(f"{self.base_url}/api/generate", json=payload)
            response.raise_for_status()
            return response.json().get("response", "")

    def embed(self, texts: list[str], **kwargs: Any) -> list[list[float]]:
        model = kwargs.get("model", self.embed_model)
        vectors: list[list[float]] = []
        with httpx.Client(timeout=self.timeout) as client:
            for text in texts:
                response = client.post(
                    f"{self.base_url}/api/embeddings",
                    json={"model": model, "prompt": text},
                )
                response.raise_for_status()
                vectors.append(response.json()["embedding"])
        return vectors
