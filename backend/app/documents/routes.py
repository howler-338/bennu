"""Document upload and management API routes."""

from flask import Blueprint, jsonify

documents_bp = Blueprint("documents", __name__)


@documents_bp.get("/")
def list_documents():
    """List uploaded documents for the current user."""
    return jsonify({"documents": []}), 200


@documents_bp.post("/")
def upload_document():
    """Upload a new document for processing."""
    return jsonify({"message": "Not implemented"}), 501


@documents_bp.delete("/<document_id>")
def delete_document(document_id: str):
    """Delete a document and its vectors."""
    return jsonify({"message": "Not implemented"}), 501
