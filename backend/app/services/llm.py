import requests
from flask import current_app


def chat(messages: list) -> str:
    ollama_host = current_app.config["OLLAMA_HOST"]
    chat_model = current_app.config["CHAT_MODEL"]
    response = requests.post(
        f"{ollama_host}/api/chat",
        json={"model": chat_model, "messages": messages, "stream": False},
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["message"]["content"]
