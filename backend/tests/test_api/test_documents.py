import io


def _txt(content="Hello world"):
    return (io.BytesIO(content.encode()), "test.txt", "text/plain")


def upload(client, headers, content="Hello world"):
    return client.post(
        "/api/documents",
        headers=headers,
        data={"file": _txt(content)},
        content_type="multipart/form-data",
    )


def test_upload_success(client, auth_headers):
    resp = upload(client, auth_headers)
    assert resp.status_code == 201
    doc = resp.get_json()["document"]
    assert doc["original_filename"] == "test.txt"
    assert doc["status"] == "pending"


def test_upload_no_file(client, auth_headers):
    resp = client.post("/api/documents", headers=auth_headers, data={}, content_type="multipart/form-data")
    assert resp.status_code == 400


def test_upload_invalid_type(client, auth_headers):
    data = {"file": (io.BytesIO(b"data"), "malware.exe", "application/octet-stream")}
    resp = client.post("/api/documents", headers=auth_headers, data=data, content_type="multipart/form-data")
    assert resp.status_code == 415


def test_upload_unauthenticated(client):
    resp = client.post("/api/documents", data={"file": _txt()}, content_type="multipart/form-data")
    assert resp.status_code == 401


def test_list_returns_own_documents(client, auth_headers):
    upload(client, auth_headers)
    upload(client, auth_headers)
    resp = client.get("/api/documents", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.get_json()["documents"]) == 2


def test_list_scoped_to_user(client, register_and_login):
    token1, _ = register_and_login("u1@test.com")
    token2, _ = register_and_login("u2@test.com")
    upload(client, {"Authorization": f"Bearer {token1}"})
    resp = client.get("/api/documents", headers={"Authorization": f"Bearer {token2}"})
    assert resp.get_json()["documents"] == []


def test_get_document(client, auth_headers):
    doc_id = upload(client, auth_headers).get_json()["document"]["id"]
    resp = client.get(f"/api/documents/{doc_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["id"] == doc_id


def test_get_missing_document(client, auth_headers):
    resp = client.get("/api/documents/00000000-0000-0000-0000-000000000000", headers=auth_headers)
    assert resp.status_code == 404


def test_get_other_users_document_returns_403(client, register_and_login):
    token1, _ = register_and_login("owner@test.com")
    token2, _ = register_and_login("other@test.com")
    doc_id = upload(client, {"Authorization": f"Bearer {token1}"}).get_json()["document"]["id"]
    resp = client.get(f"/api/documents/{doc_id}", headers={"Authorization": f"Bearer {token2}"})
    assert resp.status_code == 403


def test_delete_document(client, auth_headers):
    doc_id = upload(client, auth_headers).get_json()["document"]["id"]
    assert client.delete(f"/api/documents/{doc_id}", headers=auth_headers).status_code == 200
    assert client.get(f"/api/documents/{doc_id}", headers=auth_headers).status_code == 404
