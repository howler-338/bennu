def test_stats_blocked_for_non_admin(client, auth_headers):
    assert client.get("/api/admin/stats", headers=auth_headers).status_code == 403


def test_stats_unauthenticated(client):
    assert client.get("/api/admin/stats").status_code == 401


def test_stats_returns_counts(client, admin_headers):
    resp = client.get("/api/admin/stats", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert set(data["documents"].keys()) == {"pending", "processing", "ready", "failed", "total"}
    assert "total" in data["users"]
    assert "active" in data["users"]


def test_list_users(client, admin_headers):
    resp = client.get("/api/admin/users", headers=admin_headers)
    assert resp.status_code == 200
    users = resp.get_json()["users"]
    assert isinstance(users, list)
    assert len(users) >= 1


def test_deactivate_user(client, admin_headers, register_and_login):
    _, user = register_and_login("target@test.com")
    resp = client.patch(f"/api/admin/users/{user['id']}", headers=admin_headers, json={"is_active": False})
    assert resp.status_code == 200
    assert resp.get_json()["is_active"] is False


def test_promote_user_to_admin(client, admin_headers, register_and_login):
    _, user = register_and_login("promote@test.com")
    resp = client.patch(f"/api/admin/users/{user['id']}", headers=admin_headers, json={"role": "admin"})
    assert resp.status_code == 200
    assert resp.get_json()["role"] == "admin"


def test_delete_user(client, admin_headers, register_and_login):
    _, user = register_and_login("todelete@test.com")
    assert client.delete(f"/api/admin/users/{user['id']}", headers=admin_headers).status_code == 200
    users = client.get("/api/admin/users", headers=admin_headers).get_json()["users"]
    assert not any(u["id"] == user["id"] for u in users)


def test_failed_documents_empty(client, admin_headers):
    resp = client.get("/api/admin/documents/failed", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.get_json()["documents"] == []
