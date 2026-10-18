import pytest
from fastapi.testclient import TestClient

import auth
from app import app

MOVIES = [
    (1, "Oldboy", "Thriller", 8.4),
    (2, "The Notebook", "Romance", 7.8),
    (3, "Parasite", "Thriller", 8.6),
    (4, "La La Land", "Romance", 8.0),
    (5, "The Conjuring", "Horror", 7.5),
]


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test.db"))
    conn = auth.get_conn()
    auth.ensure_schema_and_seed(conn)
    conn.execute(
        "CREATE TABLE movie (id INTEGER PRIMARY KEY, title TEXT NOT NULL, "
        "genre TEXT NOT NULL, rating REAL NOT NULL)"
    )
    conn.executemany("INSERT INTO movie VALUES (?, ?, ?, ?)", MOVIES)
    conn.commit()
    conn.close()
    return TestClient(app)


def auth_headers(client):
    token = client.post(
        "/api/v1/auth/login",
        json={"email": auth.TEST_EMAIL, "password": auth.TEST_PASSWORD},
    ).json()["access_token"]
    profile_id = client.get(
        "/api/v1/profiles", headers={"Authorization": f"Bearer {token}"}
    ).json()[0]["id"]
    return {"Authorization": f"Bearer {token}", "X-Profile-Id": str(profile_id)}


def test_genres_requires_token(client):
    assert client.get("/api/v1/recommendations/setup/genres").status_code == 401


def test_genres_requires_profile_header(client):
    headers = {"Authorization": auth_headers(client)["Authorization"]}
    res = client.get("/api/v1/recommendations/setup/genres", headers=headers)
    assert res.status_code == 400


def test_genres_lists_each_genre_once(client):
    res = client.get("/api/v1/recommendations/setup/genres", headers=auth_headers(client))
    assert res.status_code == 200
    assert sorted(g["id"] for g in res.json()) == ["Horror", "Romance", "Thriller"]


def test_recommendations_filtered_by_genre_returns_only_that_genre(client):
    res = client.get(
        "/api/v1/recommendations?genre_id=Thriller", headers=auth_headers(client)
    )
    assert res.status_code == 200
    movies = res.json()
    assert len(movies) == 2
    assert {m["genre"] for m in movies} == {"Thriller"}


def test_recommendations_without_genre_returns_all_movies(client):
    res = client.get("/api/v1/recommendations", headers=auth_headers(client))
    assert res.status_code == 200
    assert len(res.json()) == len(MOVIES)


def test_recommendations_for_unknown_genre_returns_empty_list(client):
    res = client.get(
        "/api/v1/recommendations?genre_id=Western", headers=auth_headers(client)
    )
    assert res.status_code == 200
    assert res.json() == []


def test_recommendations_are_limited_to_10(client):
    conn = auth.get_conn()
    conn.executemany(
        "INSERT INTO movie VALUES (?, ?, ?, ?)",
        [(100 + i, f"Extra {i}", "Drama", 7.0) for i in range(11)],
    )
    conn.commit()
    conn.close()
    res = client.get(
        "/api/v1/recommendations?genre_id=Drama", headers=auth_headers(client)
    )
    assert len(res.json()) == 10  # BR3


def test_recommendations_exclude_movies_rated_below_6(client):
    conn = auth.get_conn()
    conn.execute("INSERT INTO movie VALUES (50, 'Weak Horror', 'Horror', 5.0)")
    conn.commit()
    conn.close()
    res = client.get(
        "/api/v1/recommendations?genre_id=Horror", headers=auth_headers(client)
    )
    assert "Weak Horror" not in [m["title"] for m in res.json()]  # BR4