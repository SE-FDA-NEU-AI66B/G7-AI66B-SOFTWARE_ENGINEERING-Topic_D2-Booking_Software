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


def test_rating_can_be_changed_without_creating_a_duplicate(client):
    headers = auth_headers(client)

    first = client.post(
        "/api/v1/ratings", headers=headers, json={"movie_id": 1, "score": 6}
    )
    second = client.post(
        "/api/v1/ratings", headers=headers, json={"movie_id": 1, "score": 9}
    )

    assert first.status_code == 201
    assert second.status_code == 201
    movie = client.get("/api/v1/movies/1", headers=headers).json()
    assert movie["user_rating"] == 9
    conn = auth.get_conn()
    count = conn.execute(
        "SELECT COUNT(*) FROM rating WHERE profile_id = ? AND movie_id = 1",
        (int(headers["X-Profile-Id"]),),
    ).fetchone()[0]
    conn.close()
    assert count == 1


def test_rating_outside_one_to_ten_returns_clear_validation_message(client):
    res = client.post(
        "/api/v1/ratings", headers=auth_headers(client),
        json={"movie_id": 1, "score": 11},
    )

    assert res.status_code == 400
    assert res.json()["detail"] == "Rating must be between 1 and 10."


def test_marking_movie_watched_excludes_it_from_recommendations(client):
    headers = auth_headers(client)
    add_preferences(headers, ratings=5)

    watched = client.post("/api/v1/movies/1/watch", headers=headers)
    movie = client.get("/api/v1/movies/1", headers=headers).json()
    recommendations = client.get("/api/v1/recommendations", headers=headers)

    assert watched.status_code == 200
    assert movie["watched"] == 1
    assert recommendations.status_code == 200
    assert 1 not in {item["id"] for item in recommendations.json()}


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


def test_marking_movie_watched_twice_is_idempotent(client):
    headers = auth_headers(client)
    assert client.post("/api/v1/movies/1/watch", headers=headers).status_code == 200
    assert client.post("/api/v1/movies/1/watch", headers=headers).status_code == 200


def test_watch_unknown_movie_returns_404(client):
    res = client.post("/api/v1/movies/999/watch", headers=auth_headers(client))
    assert res.status_code == 404


def test_rating_unknown_movie_returns_404(client):
    res = client.post("/api/v1/ratings", headers=auth_headers(client),
                      json={"movie_id": 999, "score": 5})
    assert res.status_code == 404


def test_rating_requires_token(client):
    res = client.post("/api/v1/ratings", json={"movie_id": 1, "score": 5})
    assert res.status_code == 401


def test_watched_movies_never_reappear_even_after_many_are_watched(client):
    headers = auth_headers(client)
    conn = auth.get_conn()
    conn.executemany(
        "INSERT INTO movie VALUES (?, ?, ?, ?, ?, ?)",
        [(100 + i, f"Extra {i}", "Thriller", 7.0, 500, f"tt9{i:06d}") for i in range(25)],
    )
    pid = int(headers["X-Profile-Id"])
    conn.executemany(
        "INSERT INTO watch_history (profile_id, movie_id) VALUES (?, ?)",
        [(pid, 100 + i) for i in range(25)],
    )
    conn.commit()
    conn.close()
    res = client.get("/api/v1/recommendations?genre_id=Thriller", headers=headers)
    assert all(m["id"] < 100 for m in res.json())  # BR1