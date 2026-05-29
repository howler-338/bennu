from flask import Flask

from app.config.settings import get_config
from app.extensions import db, jwt, migrate


def create_app(env: str = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(get_config(env))

    register_extensions(app)
    register_blueprints(app)

    return app


def register_extensions(app: Flask) -> None:
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)


def register_blueprints(app: Flask) -> None:
    from app.api.health import health_bp
    from app.auth.routes import auth_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
