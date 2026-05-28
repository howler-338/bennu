"""API blueprint registration."""

from flask import Flask

from app.api.routes import api_bp


def register_blueprints(app: Flask) -> None:
    """Register all API blueprints on the application."""
    app.register_blueprint(api_bp, url_prefix="/api/v1")
