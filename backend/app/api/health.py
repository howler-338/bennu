from flask_smorest import Blueprint
from marshmallow import Schema, fields

health_bp = Blueprint("health", __name__, url_prefix="/api", description="Health check")


class HealthSchema(Schema):
    status = fields.String()


@health_bp.get("/health")
@health_bp.response(200, HealthSchema)
def health_check():
    return {"status": "ok"}
