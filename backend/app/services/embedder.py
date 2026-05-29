import requests
from flask import current_app


def embed_text(text: str) -> list:
    ollama_host = current_app.config["OLLAMA_HOST"]
    embed_model = current_app.config["EMBED_MODEL"]
    response = requests.post(
        f"{ollama_host}/api/embeddings",
        json={"model": embed_model, "prompt": text},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["embedding"]
