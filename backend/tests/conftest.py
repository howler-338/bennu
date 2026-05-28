"""Pytest fixtures."""

import pytest

from app import create_app, db


@pytest.fixture
def app():
    """Flask application configured for testing."""
    application = create_app("testing")
    with application.app_context():
        db.create_all()
        yield application
        db.drop_all()


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()
