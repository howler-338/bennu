from marshmallow import Schema, fields


class HistoryMessageSchema(Schema):
    role = fields.String(required=True)
    content = fields.String(required=True)


class ChatQuerySchema(Schema):
    message = fields.String(required=True)
    history = fields.List(fields.Nested(HistoryMessageSchema), load_default=[])
    limit = fields.Integer(load_default=5)


class SourceSchema(Schema):
    document_id = fields.String(dump_only=True)
    filename = fields.String(dump_only=True)
    chunk_index = fields.Integer(dump_only=True)


class ChatResponseSchema(Schema):
    reply = fields.String(dump_only=True)
    sources = fields.List(fields.Nested(SourceSchema), dump_only=True)
