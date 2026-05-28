"""Embedding and semantic search API routes."""

from flask import Blueprint, jsonify

embeddings_bp = Blueprint("embeddings", __name__)


@embeddings_bp.post("/search")
def semantic_search():
    """Search document chunks by vector similarity."""
    return jsonify({"results": []}), 200
