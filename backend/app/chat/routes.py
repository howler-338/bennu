"""RAG chat API routes."""

from flask import Blueprint, jsonify

chat_bp = Blueprint("chat", __name__)


@chat_bp.get("/conversations")
def list_conversations():
    """List chat conversations for the current user."""
    return jsonify({"conversations": []}), 200


@chat_bp.post("/")
def send_message():
    """Send a message and receive a RAG-augmented response."""
    return jsonify({"message": "Not implemented"}), 501
