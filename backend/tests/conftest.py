from unittest.mock import patch

import pytest
from sqlalchemy import create_engine, text

from app import create_app
from app.extensions import db as _db


@pytest.fixture(scope="session")
def app():
    flask_app = create_app("testing")
    db_url = flask_app.config["SQLALCHEMY_DATABASE_URI"]
    base_url = db_url.rsplit("/", 1)[0]

    # Create the test database from scratch
    engine = create_engine(f"{base_url}/postgres", isolation_level="AUTOCOMMIT")
    with engine.connect() as conn:
        conn.execute(text("DROP DATABASE IF EXISTS bennu_test"))
        conn.execute(text("CREATE DATABASE bennu_test"))
    engine.dispose()

    with flask_app.app_context():
        _db.session.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        _db.session.commit()
        _db.create_all()

    yield flask_app

    with flask_app.app_context():
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def clean_db(app):
    yield
    with app.app_context():
        _db.session.rollback()
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()


@pytest.fixture(autouse=True)
def mock_celery():
    """Prevent Celery tasks from dispatching during tests."""
    with patch("app.workers.document_tasks.process_document.delay"):
        yield


@pytest.fixture()
def register_and_login(client):
    def _do(email="user@test.com", password="password123"):
        resp = client.post("/api/auth/register", json={"email": email, "password": password})
        data = resp.get_json()
        return data["access_token"], data["user"]
    return _do


@pytest.fixture()
def auth_headers(register_and_login):
    token, _ = register_and_login()
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def admin_headers(client, register_and_login):
    from app.auth.models import User, UserRole
    token, user = register_and_login(email="admin@test.com")
    with client.application.app_context():
        u = _db.session.get(User, user["id"])
        u.role = UserRole.ADMIN
        _db.session.commit()
    return {"Authorization": f"Bearer {token}"}
