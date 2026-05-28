"""Flask application factory."""

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from app.config import get_config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_name: str | None = None) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(get_config(config_name))

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, origins=app.config.get("CORS_ORIGINS", ["http://localhost:5173"]))

    from app.api import register_blueprints

    register_blueprints(app)

    @app.get("/health")
    def health():
        return {"status": "ok"}, 200

    return app
