"""Shared fixtures for API tests."""

import pytest
from fastapi.testclient import TestClient

import auth
from app import app

MOVIES = [
    (1, "Oldboy", "Thriller", 8.3, 735723, "tt0364569"),
    (2, "The Notebook", "Romance", 7.8, 704780, "tt0332280"),
    (3, "Parasite", "Thriller", 8.5, 1203068, "tt6751668"),
    (4, "La La Land", "Romance", 8.0, 781879, "tt3783958"),
    (5, "The Conjuring", "Horror", 7.5, 635470, "tt1457767"),
    (6, "Get Out", "Horror", 7.8, 842084, "tt5052448"),
    (7, "The Shining", "Horror", 8.4, 1248440, "tt0081505"),
    (8, "The Exorcist", "Horror", 8.1, 507048, "tt0070047"),
    (9, "Inception", "Thriller", 8.8, 2880387, "tt1375666"),
    (10, "Titanic", "Romance", 8.0, 1417134, "tt0120338"),
    (11, "Memento", "Thriller", 8.4, 1463441, "tt0209144"),
    (12, "Prisoners", "Thriller", 8.2, 963812, "tt1392214"),
]


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """Provide an API client backed by an isolated, fully seeded SQLite database."""
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test.db"))
    conn = auth.get_conn()
    auth.ensure_schema_and_seed(conn)
    conn.executescript(
        """
        CREATE TABLE movie (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            genre TEXT NOT NULL,
            rating REAL NOT NULL,
            rating_count INTEGER NOT NULL,
            imdb_id TEXT NOT NULL
        );
        CREATE TABLE rating (
            id INTEGER PRIMARY KEY,
            profile_id INTEGER NOT NULL,
            movie_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            UNIQUE(profile_id, movie_id)
        );
        CREATE TABLE watch_history (
            profile_id INTEGER NOT NULL,
            movie_id INTEGER NOT NULL,
            PRIMARY KEY(profile_id, movie_id)
        );
        """
    )
    conn.executemany("INSERT INTO movie VALUES (?, ?, ?, ?, ?, ?)", MOVIES)

    # Used by profile tests to verify account-scoped access.
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


@pytest.fixture()
def auth_headers(client):
    """Return bearer and selected-profile headers for the seeded demo account."""
    token = client.post(
        "/api/v1/auth/login",
        json={"email": auth.TEST_EMAIL, "password": auth.TEST_PASSWORD},
    ).json()["access_token"]
    profile_id = client.get(
        "/api/v1/profiles", headers={"Authorization": f"Bearer {token}"}
    ).json()[0]["id"]
    return {"Authorization": f"Bearer {token}", "X-Profile-Id": str(profile_id)}


def add_preferences(headers, *, ratings=5, watched=0):
    """Insert ratings and watch history for the profile in the supplied headers."""
    profile_id = int(headers["X-Profile-Id"])
    conn = auth.get_conn()
    try:
        conn.executemany(
            "INSERT INTO rating (profile_id, movie_id, score) VALUES (?, ?, ?)",
            [(profile_id, movie_id, 8) for movie_id in range(1, ratings + 1)],
        )
        conn.executemany(
            "INSERT INTO watch_history (profile_id, movie_id) VALUES (?, ?)",
            [
                (profile_id, movie_id)
                for movie_id in range(ratings + 1, ratings + watched + 1)
            ],
        )
        conn.commit()
    finally:
        conn.close()
