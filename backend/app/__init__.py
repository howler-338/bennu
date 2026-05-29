from flask import Flask

from app.config.settings import get_config
from app.extensions import db, jwt, migrate, smorest_api
from app.workers.celery_app import celery_init_app


def create_app(env: str = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(get_config(env))

    register_extensions(app)
    register_blueprints(app)
    celery_init_app(app)

    return app


def register_extensions(app: Flask) -> None:
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    smorest_api.init_app(app)


def register_blueprints(app: Flask) -> None:
    from app.api.health import health_bp
    from app.auth.routes import auth_bp
    from app.documents.routes import documents_bp
    import app.embeddings.models  # noqa: ensure DocumentChunk is in SQLAlchemy metadata

    smorest_api.register_blueprint(health_bp)
    smorest_api.register_blueprint(auth_bp)
    smorest_api.register_blueprint(documents_bp)
