from fastapi.testclient import TestClient


def test_login_success(client: TestClient):
    resp = client.post(
        "/api/v1/auth/login", data={"username": "commander", "password": "commander123"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["tokenType"] == "bearer"
    assert body["user"]["username"] == "commander"
    assert body["user"]["role"] == "COMMANDER"
    assert body["accessToken"]


def test_login_wrong_password(client: TestClient):
    resp = client.post("/api/v1/auth/login", data={"username": "commander", "password": "wrong"})
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "UNAUTHORIZED"


def test_login_unknown_user(client: TestClient):
    resp = client.post("/api/v1/auth/login", data={"username": "nobody", "password": "x"})
    assert resp.status_code == 401


def test_me_requires_token(client: TestClient):
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401


def test_me_with_valid_token(client: TestClient, auth_headers):
    headers = auth_headers("planner", "planner123")
    resp = client.get("/api/v1/auth/me", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["username"] == "planner"


def test_me_rejects_garbage_token(client: TestClient):
    resp = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert resp.status_code == 401
