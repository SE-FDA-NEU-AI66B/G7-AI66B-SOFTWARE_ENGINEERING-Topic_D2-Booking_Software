import pytest
from fastapi.testclient import TestClient

import auth
from app import app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test.db"))
    conn = auth.get_conn()
    auth.ensure_schema_and_seed(conn)
    # A second account whose profile must never be reachable from the test account.
    cur = conn.execute(
        "INSERT INTO account (email, password_hash) VALUES (?, ?)",
        ("other@smartcine.test", auth.hash_password("Other@1234")),
    )
    conn.execute(
        "INSERT INTO profile (account_id, name, avatar_color) VALUES (?, 'Stranger', '#fff')",
        (cur.lastrowid,),
    )
    conn.commit()
    conn.close()
    return TestClient(app)


def token(client):
    res = client.post(
        "/api/v1/auth/login",
        json={"email": auth.TEST_EMAIL, "password": auth.TEST_PASSWORD},
    )
    return res.json()["access_token"]


def bearer(client):
    return {"Authorization": f"Bearer {token(client)}"}


def stranger_profile_id():
    conn = auth.get_conn()
    pid = conn.execute("SELECT id FROM profile WHERE name = 'Stranger'").fetchone()["id"]
    conn.close()
    return pid


def test_list_profiles_requires_token(client):
    assert client.get("/api/v1/profiles").status_code == 401


def test_list_profiles_returns_only_own_profiles(client):
    res = client.get("/api/v1/profiles", headers=bearer(client))
    assert res.status_code == 200
    assert [p["name"] for p in res.json()] == ["Alex", "Sam"]


def test_invalid_token_returns_401(client):
    res = client.get("/api/v1/profiles", headers={"Authorization": "Bearer nonsense"})
    assert res.status_code == 401


def test_select_own_profile_returns_200(client):
    own_id = client.get("/api/v1/profiles", headers=bearer(client)).json()[0]["id"]
    res = client.post(
        "/api/v1/profiles/select", json={"profile_id": own_id}, headers=bearer(client)
    )
    assert res.status_code == 200
    assert res.json()["name"] == "Alex"


def test_select_profile_of_another_account_returns_404(client):
    res = client.post(
        "/api/v1/profiles/select",
        json={"profile_id": stranger_profile_id()},
        headers=bearer(client),
    )
    assert res.status_code == 404


def test_select_without_profile_id_returns_400(client):
    res = client.post("/api/v1/profiles/select", json={}, headers=bearer(client))
    assert res.status_code == 400


def test_scoped_endpoint_needs_profile_header(client):
    assert client.get("/api/v1/profiles/me", headers=bearer(client)).status_code == 400


def test_scoped_endpoint_rejects_profile_of_another_account(client):
    headers = {**bearer(client), "X-Profile-Id": str(stranger_profile_id())}
    assert client.get("/api/v1/profiles/me", headers=headers).status_code == 404


def test_scoped_endpoint_returns_selected_profile(client):
    sam_id = client.get("/api/v1/profiles", headers=bearer(client)).json()[1]["id"]
    headers = {**bearer(client), "X-Profile-Id": str(sam_id)}
    res = client.get("/api/v1/profiles/me", headers=headers)
    assert res.status_code == 200
    assert res.json()["name"] == "Sam"