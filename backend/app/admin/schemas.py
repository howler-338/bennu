from marshmallow import Schema, fields

from app.auth.models import UserRole
from app.documents.models import DocumentStatus


class AdminUserSchema(Schema):
    id = fields.String(dump_only=True)
    email = fields.Email(dump_only=True)
    is_active = fields.Boolean(dump_only=True)
    role = fields.Enum(UserRole, by_value=True, dump_only=True)
    created_at = fields.DateTime(dump_only=True)


class AdminUserListSchema(Schema):
    users = fields.List(fields.Nested(AdminUserSchema), dump_only=True)
    total = fields.Integer(dump_only=True)


class UpdateUserSchema(Schema):
    is_active = fields.Boolean()
    role = fields.Enum(UserRole, by_value=True)


class DocumentStatsSchema(Schema):
    pending = fields.Integer(dump_only=True)
    processing = fields.Integer(dump_only=True)
    ready = fields.Integer(dump_only=True)
    failed = fields.Integer(dump_only=True)
    total = fields.Integer(dump_only=True)


class UserStatsSchema(Schema):
    total = fields.Integer(dump_only=True)
    active = fields.Integer(dump_only=True)


class StatsSchema(Schema):
    documents = fields.Nested(DocumentStatsSchema, dump_only=True)
    users = fields.Nested(UserStatsSchema, dump_only=True)


class FailedDocumentSchema(Schema):
    id = fields.String(dump_only=True)
    original_filename = fields.String(dump_only=True)
    owner_email = fields.String(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class FailedDocumentsSchema(Schema):
    documents = fields.List(fields.Nested(FailedDocumentSchema), dump_only=True)


class AdminMessageSchema(Schema):
    message = fields.String(dump_only=True)
