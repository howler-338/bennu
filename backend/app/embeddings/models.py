from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import UUID

from app.extensions import db
from app.models import BaseModel


class DocumentChunk(BaseModel):
    __tablename__ = "document_chunks"

    document_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_index = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    embedding = db.Column(Vector(768), nullable=True)

    document = db.relationship(
        "Document",
        backref=db.backref("chunks", lazy="dynamic", cascade="all, delete-orphan"),
    )
