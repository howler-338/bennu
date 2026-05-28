"""RAG pipeline API routes."""

from flask import Blueprint, jsonify

rag_bp = Blueprint("rag", __name__)


@rag_bp.post("/query")
def rag_query():
    """Run retrieval-augmented generation for a query."""
    return jsonify({"message": "Not implemented"}), 501
