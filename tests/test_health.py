"""Tests for GET /health (Sprint 5, issue #119).

The host (Render) calls /health to decide whether the app is alive:
200 when the app can read the database, 503 when it cannot.
"""

HEALTH_URL = "/health"


def test_health_returns_200_when_database_is_readable(client):
    res = client.get(HEALTH_URL)

    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_health_returns_503_when_database_is_empty(client, tmp_path, monkeypatch):
    empty_db = tmp_path / "empty.db"
    empty_db.touch()
    monkeypatch.setenv("DB_PATH", str(empty_db))

    res = client.get(HEALTH_URL)

    assert res.status_code == 503
    assert res.json() == {"status": "unavailable"}