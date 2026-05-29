import os
import uuid

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from werkzeug.utils import secure_filename

from app.documents.models import Document, DocumentStatus
from app.extensions import db

documents_bp = Blueprint("documents", __name__, url_prefix="/api/documents")

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "text/plain",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

ALLOWED_EXTENSIONS = {"pdf", "txt", "docx"}


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@documents_bp.post("")
@jwt_required()
def upload_document():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    if not file.filename:
        return jsonify({"error": "No file selected"}), 400

    if not _allowed_file(file.filename):
        return jsonify({"error": f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"}), 415

    user_id = get_jwt_identity()
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)

    original_filename = secure_filename(file.filename)
    extension = original_filename.rsplit(".", 1)[1].lower()
    stored_filename = f"{uuid.uuid4()}.{extension}"
    file_path = os.path.join(upload_folder, stored_filename)

    file.save(file_path)
    file_size = os.path.getsize(file_path)

    mime_type = file.mimetype or "application/octet-stream"

    document = Document(
        user_id=user_id,
        original_filename=original_filename,
        stored_filename=stored_filename,
        file_path=file_path,
        file_size=file_size,
        mime_type=mime_type,
        status=DocumentStatus.PENDING,
    )
    db.session.add(document)
    db.session.commit()

    return jsonify({"message": "Document uploaded successfully", "document": document.to_dict()}), 201


@documents_bp.get("")
@jwt_required()
def list_documents():
    user_id = get_jwt_identity()
    documents = Document.query.filter_by(user_id=user_id).order_by(Document.created_at.desc()).all()
    return jsonify({"documents": [doc.to_dict() for doc in documents]}), 200


@documents_bp.get("/<uuid:document_id>")
@jwt_required()
def get_document(document_id):
    user_id = get_jwt_identity()
    document = db.session.get(Document, document_id)

    if not document:
        return jsonify({"error": "Document not found"}), 404

    if str(document.user_id) != user_id:
        return jsonify({"error": "Forbidden"}), 403

    return jsonify({"document": document.to_dict()}), 200


@documents_bp.delete("/<uuid:document_id>")
@jwt_required()
def delete_document(document_id):
    user_id = get_jwt_identity()
    document = db.session.get(Document, document_id)

    if not document:
        return jsonify({"error": "Document not found"}), 404

    if str(document.user_id) != user_id:
        return jsonify({"error": "Forbidden"}), 403

    if os.path.exists(document.file_path):
        os.remove(document.file_path)

    db.session.delete(document)
    db.session.commit()

    return jsonify({"message": "Document deleted successfully"}), 200
