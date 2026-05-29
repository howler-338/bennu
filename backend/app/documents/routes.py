import os
import uuid

from flask import current_app, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_smorest import Blueprint, abort
from werkzeug.utils import secure_filename

from app.documents.models import Document, DocumentStatus
from app.documents.schemas import DocumentListSchema, DocumentSchema, DocumentUploadedSchema, MessageSchema
from app.extensions import db

documents_bp = Blueprint("documents", __name__, url_prefix="/api/documents", description="Document management")

ALLOWED_EXTENSIONS = {"pdf", "txt", "docx"}


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@documents_bp.post("")
@jwt_required()
@documents_bp.response(201, DocumentUploadedSchema)
def upload_document():
    if "file" not in request.files:
        abort(400, message="No file provided")

    file = request.files["file"]

    if not file.filename:
        abort(400, message="No file selected")

    if not _allowed_file(file.filename):
        abort(415, message=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}")

    user_id = get_jwt_identity()
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)

    original_filename = secure_filename(file.filename)
    extension = original_filename.rsplit(".", 1)[1].lower()
    stored_filename = f"{uuid.uuid4()}.{extension}"
    file_path = os.path.join(upload_folder, stored_filename)

    file.save(file_path)

    document = Document(
        user_id=user_id,
        original_filename=original_filename,
        stored_filename=stored_filename,
        file_path=file_path,
        file_size=os.path.getsize(file_path),
        mime_type=file.mimetype or "application/octet-stream",
        status=DocumentStatus.PENDING,
    )
    db.session.add(document)
    db.session.commit()

    from app.workers.document_tasks import process_document
    process_document.delay(str(document.id))

    return {"message": "Document uploaded successfully", "document": document}


@documents_bp.get("")
@jwt_required()
@documents_bp.response(200, DocumentListSchema)
def list_documents():
    user_id = get_jwt_identity()
    documents = Document.query.filter_by(user_id=user_id).order_by(Document.created_at.desc()).all()
    return {"documents": documents}


@documents_bp.get("/<uuid:document_id>")
@jwt_required()
@documents_bp.response(200, DocumentSchema)
def get_document(document_id):
    user_id = get_jwt_identity()
    document = db.session.get(Document, document_id)

    if not document:
        abort(404, message="Document not found")

    if str(document.user_id) != user_id:
        abort(403, message="Forbidden")

    return document


@documents_bp.delete("/<uuid:document_id>")
@jwt_required()
@documents_bp.response(200, MessageSchema)
def delete_document(document_id):
    user_id = get_jwt_identity()
    document = db.session.get(Document, document_id)

    if not document:
        abort(404, message="Document not found")

    if str(document.user_id) != user_id:
        abort(403, message="Forbidden")

    if os.path.exists(document.file_path):
        os.remove(document.file_path)

    db.session.delete(document)
    db.session.commit()

    return {"message": "Document deleted successfully"}
