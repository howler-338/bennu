from marshmallow import Schema, fields

from app.documents.schemas import DocumentSchema


class SearchQuerySchema(Schema):
    query = fields.String(required=True)
    limit = fields.Integer(load_default=5)


class SearchResultItemSchema(Schema):
    content = fields.String(dump_only=True)
    similarity = fields.Float(dump_only=True)
    chunk_index = fields.Integer(dump_only=True)
    document = fields.Nested(DocumentSchema, dump_only=True)


class SearchResultsSchema(Schema):
    results = fields.List(fields.Nested(SearchResultItemSchema), dump_only=True)
