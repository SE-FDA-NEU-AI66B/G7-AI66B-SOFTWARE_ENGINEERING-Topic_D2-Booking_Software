import pytest
from fastapi.testclient import TestClient

import auth
from app import app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test.db"))
    conn = auth.get_conn()
    auth.ensure_schema_and_seed(conn)
    conn.close()
    return TestClient(app)


def login(client, email, password):
    return client.post("/api/v1/auth/login", json={"email": email, "password": password})


def test_login_success_returns_token_and_profiles(client):
    res = login(client, auth.TEST_EMAIL, auth.TEST_PASSWORD)
    assert res.status_code == 200
    body = res.json()
    assert body["access_token"]
    assert [p["name"] for p in body["profiles"]] == ["Alex", "Sam"]


def test_login_wrong_password_returns_401(client):
    assert login(client, auth.TEST_EMAIL, "wrong").status_code == 401


def test_login_unknown_email_returns_401(client):
    assert login(client, "nobody@smartcine.test", "whatever").status_code == 401


def test_login_missing_fields_returns_400(client):
    assert login(client, "", "").status_code == 400