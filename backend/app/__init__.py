from flask import Flask

from app.config.settings import get_config


def create_app(env: str = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(get_config(env))

    register_blueprints(app)

    return app


def register_blueprints(app: Flask) -> None:
    from app.api.health import health_bp

    app.register_blueprint(health_bp)
