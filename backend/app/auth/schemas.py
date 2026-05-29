from marshmallow import Schema, fields, validate

from app.auth.models import UserRole


class RegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8), load_only=True)


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)


class UserSchema(Schema):
    id = fields.String(dump_only=True)
    email = fields.Email(dump_only=True)
    is_active = fields.Boolean(dump_only=True)
    role = fields.Enum(UserRole, by_value=True, dump_only=True)
    created_at = fields.DateTime(dump_only=True)


class TokenSchema(Schema):
    access_token = fields.String(dump_only=True)
    refresh_token = fields.String(dump_only=True)
    user = fields.Nested(UserSchema, dump_only=True)


class AccessTokenSchema(Schema):
    access_token = fields.String(dump_only=True)


class AuthMessageSchema(Schema):
    message = fields.String(dump_only=True)
