from sqlalchemy import func
from flask_smorest import Blueprint

from app.admin.decorators import admin_required
from app.admin.schemas import (
    AdminMessageSchema,
    AdminUserListSchema,
    AdminUserSchema,
    FailedDocumentsSchema,
    StatsSchema,
    UpdateUserSchema,
)
from app.auth.models import User, UserRole
from app.documents.models import Document, DocumentStatus
from app.extensions import db

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin", description="Admin dashboard")


@admin_bp.get("/users")
@admin_required
@admin_bp.response(200, AdminUserListSchema)
def list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return {"users": users, "total": len(users)}


@admin_bp.patch("/users/<uuid:user_id>")
@admin_required
@admin_bp.arguments(UpdateUserSchema)
@admin_bp.response(200, AdminUserSchema)
def update_user(args, user_id):
    user = db.session.get(User, user_id)
    if not user:
        admin_bp.abort(404, message="User not found")
    if "is_active" in args:
        user.is_active = args["is_active"]
    if "role" in args:
        user.role = args["role"]
    db.session.commit()
    return user


@admin_bp.delete("/users/<uuid:user_id>")
@admin_required
@admin_bp.response(200, AdminMessageSchema)
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        admin_bp.abort(404, message="User not found")
    db.session.delete(user)
    db.session.commit()
    return {"message": "User deleted"}


@admin_bp.get("/stats")
@admin_required
@admin_bp.response(200, StatsSchema)
def stats():
    doc_counts = dict(
        db.session.query(Document.status, func.count(Document.id))
        .group_by(Document.status)
        .all()
    )
    return {
        "documents": {
            "pending": doc_counts.get(DocumentStatus.PENDING, 0),
            "processing": doc_counts.get(DocumentStatus.PROCESSING, 0),
            "ready": doc_counts.get(DocumentStatus.READY, 0),
            "failed": doc_counts.get(DocumentStatus.FAILED, 0),
            "total": sum(doc_counts.values()),
        },
        "users": {
            "total": User.query.count(),
            "active": User.query.filter_by(is_active=True).count(),
        },
    }


@admin_bp.get("/documents/failed")
@admin_required
@admin_bp.response(200, FailedDocumentsSchema)
def failed_documents():
    rows = (
        db.session.query(Document, User.email)
        .join(User, Document.user_id == User.id)
        .filter(Document.status == DocumentStatus.FAILED)
        .order_by(Document.updated_at.desc())
        .all()
    )
    return {
        "documents": [
            {
                "id": str(doc.id),
                "original_filename": doc.original_filename,
                "owner_email": email,
                "created_at": doc.created_at,
                "updated_at": doc.updated_at,
            }
            for doc, email in rows
        ]
    }


@admin_bp.post("/documents/<uuid:document_id>/reprocess")
@admin_required
@admin_bp.response(200, AdminMessageSchema)
def reprocess_document(document_id):
    document = db.session.get(Document, document_id)
    if not document:
        admin_bp.abort(404, message="Document not found")
    document.status = DocumentStatus.PENDING
    db.session.commit()
    from app.workers.document_tasks import process_document
    process_document.delay(str(document_id))
    return {"message": "Document queued for reprocessing"}
