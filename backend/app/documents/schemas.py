from marshmallow import Schema, fields

from app.documents.models import DocumentStatus


class DocumentSchema(Schema):
    id = fields.String(dump_only=True)
    original_filename = fields.String(dump_only=True)
    file_size = fields.Integer(dump_only=True)
    mime_type = fields.String(dump_only=True)
    status = fields.Enum(DocumentStatus, by_value=True, dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class DocumentListSchema(Schema):
    documents = fields.List(fields.Nested(DocumentSchema), dump_only=True)


class MessageSchema(Schema):
    message = fields.String(dump_only=True)


class DocumentUploadedSchema(Schema):
    message = fields.String(dump_only=True)
    document = fields.Nested(DocumentSchema, dump_only=True)
