import uuid

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID

from app.extensions import db


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = db.Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = db.Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
