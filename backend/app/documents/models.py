import enum

from sqlalchemy.dialects.postgresql import UUID

from app.extensions import db
from app.models import BaseModel


class DocumentStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class Document(BaseModel):
    __tablename__ = "documents"

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False, unique=True)
    file_path = db.Column(db.String(512), nullable=False)
    file_size = db.Column(db.BigInteger, nullable=False)
    mime_type = db.Column(db.String(128), nullable=False)
    status = db.Column(db.Enum(DocumentStatus), default=DocumentStatus.PENDING, nullable=False)

    user = db.relationship("User", backref=db.backref("documents", lazy="dynamic"))

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "original_filename": self.original_filename,
            "file_size": self.file_size,
            "mime_type": self.mime_type,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
