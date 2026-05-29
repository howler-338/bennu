def test_register_success(client):
    resp = client.post("/api/auth/register", json={"email": "new@test.com", "password": "password123"})
    assert resp.status_code == 201
    data = resp.get_json()
    assert "access_token" in data
    assert data["user"]["email"] == "new@test.com"
    assert data["user"]["role"] == "user"


def test_register_duplicate_email(client):
    client.post("/api/auth/register", json={"email": "dup@test.com", "password": "password123"})
    resp = client.post("/api/auth/register", json={"email": "dup@test.com", "password": "password123"})
    assert resp.status_code == 409


def test_register_short_password(client):
    resp = client.post("/api/auth/register", json={"email": "x@test.com", "password": "short"})
    assert resp.status_code == 422


def test_login_success(client):
    client.post("/api/auth/register", json={"email": "login@test.com", "password": "password123"})
    resp = client.post("/api/auth/login", json={"email": "login@test.com", "password": "password123"})
    assert resp.status_code == 200
    assert "access_token" in resp.get_json()


def test_login_wrong_password(client):
    client.post("/api/auth/register", json={"email": "wp@test.com", "password": "password123"})
    resp = client.post("/api/auth/login", json={"email": "wp@test.com", "password": "wrongpass"})
    assert resp.status_code == 401


def test_login_unknown_email(client):
    resp = client.post("/api/auth/login", json={"email": "nobody@test.com", "password": "password123"})
    assert resp.status_code == 401


def test_me_returns_current_user(client, auth_headers):
    resp = client.get("/api/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert "email" in resp.get_json()


def test_me_unauthenticated(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_refresh_returns_new_token(client):
    reg = client.post("/api/auth/register", json={"email": "refresh@test.com", "password": "password123"})
    refresh_token = reg.get_json()["refresh_token"]
    resp = client.post("/api/auth/refresh", headers={"Authorization": f"Bearer {refresh_token}"})
    assert resp.status_code == 200
    assert "access_token" in resp.get_json()
