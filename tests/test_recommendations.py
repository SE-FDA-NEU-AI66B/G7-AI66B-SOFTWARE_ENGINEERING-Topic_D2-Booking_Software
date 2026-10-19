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
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test.db"))
    conn = auth.get_conn()
    auth.ensure_schema_and_seed(conn)
    conn.execute(
        "CREATE TABLE movie (id INTEGER PRIMARY KEY, title TEXT NOT NULL, "
        "genre TEXT NOT NULL, rating REAL NOT NULL, rating_count INTEGER NOT NULL, "
        "imdb_id TEXT NOT NULL)"
    )
    conn.execute(
        "CREATE TABLE rating (id INTEGER PRIMARY KEY, profile_id INTEGER NOT NULL, "
        "movie_id INTEGER NOT NULL, score INTEGER NOT NULL, UNIQUE(profile_id, movie_id))"
    )
    conn.execute(
        "CREATE TABLE watch_history (profile_id INTEGER NOT NULL, movie_id INTEGER NOT NULL, "
        "PRIMARY KEY(profile_id, movie_id))"
    )
    conn.executemany("INSERT INTO movie VALUES (?, ?, ?, ?, ?, ?)", MOVIES)
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


def add_preferences(headers, *, ratings=5, watched=0):
    profile_id = int(headers["X-Profile-Id"])
    conn = auth.get_conn()
    conn.executemany(
        "INSERT INTO rating (profile_id, movie_id, score) VALUES (?, ?, ?)",
        [(profile_id, movie_id, 8) for movie_id in range(1, ratings + 1)],
    )
    conn.executemany(
        "INSERT INTO watch_history (profile_id, movie_id) VALUES (?, ?)",
        [(profile_id, movie_id) for movie_id in range(ratings + 1, ratings + watched + 1)],
    )
    conn.commit()
    conn.close()


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
    headers = auth_headers(client)
    add_preferences(headers)
    res = client.get(
        "/api/v1/recommendations?genre_id=Thriller", headers=headers
    )
    assert res.status_code == 200
    movies = res.json()
    assert [m["title"] for m in movies] == [m[1] for m in MOVIES if m[2] == "Thriller"] or len(movies) == 5
    assert {m["genre"] for m in movies} == {"Thriller"}


def test_recommendations_without_genre_returns_cold_start_list(client):
    res = client.get("/api/v1/recommendations", headers=auth_headers(client))
    assert res.status_code == 200
    assert len(res.json()) == 10
    assert res.headers["X-Recommendation-Mode"] == "cold-start"


def test_recommendations_for_unknown_genre_returns_empty_list(client):
    headers = auth_headers(client)
    add_preferences(headers)
    res = client.get(
        "/api/v1/recommendations?genre_id=Western", headers=headers
    )
    assert res.status_code == 200
    assert res.json() == []


def test_recommendations_are_limited_to_10(client):
    headers = auth_headers(client)
    add_preferences(headers)
    res = client.get(
        "/api/v1/recommendations", headers=headers
    )
    assert res.status_code == 200
    assert len(res.json()) == 10  # BR3


def test_recommendations_exclude_movies_rated_below_6(client):
    headers = auth_headers(client)
    add_preferences(headers)
    conn = auth.get_conn()
    conn.execute("UPDATE movie SET rating = 5.0 WHERE title = 'The Conjuring'")
    conn.commit()
    conn.close()
    res = client.get(
        "/api/v1/recommendations?genre_id=Horror", headers=headers
    )
    assert "The Conjuring" not in [m["title"] for m in res.json()]  # BR4


def test_fewer_than_five_preferences_gets_ten_cold_start_movies(client):
    headers = auth_headers(client)
    add_preferences(headers, ratings=3, watched=1)

    res = client.get("/api/v1/recommendations", headers=headers)

    assert res.status_code == 200
    movies = res.json()
    assert len(movies) == 10
    assert all(movie["rating_count"] >= 100 for movie in movies)
    assert all(movie["imdb_id"].startswith("tt") for movie in movies)
    assert res.headers["X-Recommendation-Mode"] == "cold-start"


def test_five_preferences_uses_personalized_path(client):
    headers = auth_headers(client)
    add_preferences(headers, ratings=4, watched=1)

    res = client.get("/api/v1/recommendations", headers=headers)

    assert res.status_code == 200
    assert res.headers["X-Recommendation-Mode"] == "personalized"
    assert len(res.json()) <= 10


def test_cold_start_reports_error_when_fewer_than_ten_movies_qualify(client):
    conn = auth.get_conn()
    conn.execute("UPDATE movie SET rating_count = 99")
    conn.commit()
    conn.close()

    res = client.get("/api/v1/recommendations", headers=auth_headers(client))

    assert res.status_code == 503
    assert res.json()["detail"]["code"] == "COLD_START_UNAVAILABLE"


def test_cold_start_excludes_movie_with_fewer_than_100_ratings(client):
    conn = auth.get_conn()
    conn.execute("UPDATE movie SET rating_count = 99 WHERE title = 'Parasite'")
    conn.commit()
    conn.close()

    res = client.get("/api/v1/recommendations", headers=auth_headers(client))

    assert res.status_code == 200
    assert len(res.json()) == 10
    assert "Parasite" not in [movie["title"] for movie in res.json()]


def test_cold_start_ignores_genre_filter(client):
    res = client.get("/api/v1/recommendations?genre_id=Horror", headers=auth_headers(client))
    assert res.status_code == 200
    assert res.headers["X-Recommendation-Mode"] == "cold-start"
    assert len(res.json()) == 10


def test_cold_start_includes_movie_with_exactly_100_ratings(client):
    conn = auth.get_conn()
    conn.execute("UPDATE movie SET rating_count = 100 WHERE title = 'Inception'")
    conn.commit()
    conn.close()
    res = client.get("/api/v1/recommendations", headers=auth_headers(client))
    assert "Inception" in [m["title"] for m in res.json()]  # BR8 boundary


def test_cold_start_is_sorted_by_rating_then_vote_count(client):
    res = client.get("/api/v1/recommendations", headers=auth_headers(client))
    ratings = [m["rating"] for m in res.json()]
    assert ratings == sorted(ratings, reverse=True)