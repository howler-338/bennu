import os

from flask import Flask, send_from_directory

from app.commands import make_admin_command
from app.config.settings import get_config
from app.extensions import db, jwt, migrate, smorest_api
from app.workers.celery_app import celery_init_app


def create_app(env: str = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(get_config(env))

    register_extensions(app)
    register_blueprints(app)
    celery_init_app(app)
    app.cli.add_command(make_admin_command)
    register_frontend(app)

    return app


def register_frontend(app: Flask) -> None:
    dist = app.config.get("FRONTEND_DIST", "")
    if not dist or not os.path.isdir(dist):
        return

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_frontend(path):
        file_path = os.path.join(dist, path)
        if path and os.path.isfile(file_path):
            return send_from_directory(dist, path)
        return send_from_directory(dist, "index.html")


def register_extensions(app: Flask) -> None:
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    smorest_api.init_app(app)


def register_blueprints(app: Flask) -> None:
    from app.admin.routes import admin_bp
    from app.api.health import health_bp
    from app.auth.routes import auth_bp
    from app.chat.routes import chat_bp
    from app.documents.routes import documents_bp
    from app.search.routes import search_bp
    import app.embeddings.models  # noqa: ensure DocumentChunk is in SQLAlchemy metadata

    smorest_api.register_blueprint(admin_bp)
    smorest_api.register_blueprint(health_bp)
    smorest_api.register_blueprint(auth_bp)
    smorest_api.register_blueprint(chat_bp)
    smorest_api.register_blueprint(documents_bp)
    smorest_api.register_blueprint(search_bp)
