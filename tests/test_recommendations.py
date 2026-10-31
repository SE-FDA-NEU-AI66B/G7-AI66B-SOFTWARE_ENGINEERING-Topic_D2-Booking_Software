from conftest import add_preferences

import auth


def test_genres_requires_token(client):
    assert client.get("/api/v1/recommendations/setup/genres").status_code == 401


def test_genres_requires_profile_header(client, auth_headers):
    headers = {"Authorization": auth_headers["Authorization"]}
    res = client.get("/api/v1/recommendations/setup/genres", headers=headers)
    assert res.status_code == 400


def test_genres_lists_each_genre_once(client, auth_headers):
    res = client.get("/api/v1/recommendations/setup/genres", headers=auth_headers)
    assert res.status_code == 200
    assert sorted(g["id"] for g in res.json()) == ["Horror", "Romance", "Thriller"]


def test_recommendations_filtered_by_genre_returns_only_that_genre(client, auth_headers):
    headers = auth_headers
    add_preferences(headers)
    res = client.get(
        "/api/v1/recommendations?genre_id=Thriller", headers=headers
    )
    assert res.status_code == 200
    movies = res.json()
    assert {m["genre"] for m in movies} == {"Thriller"}


def test_tc07_zero_preferences_returns_ten_qualified_cold_start_movies(
    client, auth_headers
):
    res = client.get("/api/v1/recommendations", headers=auth_headers)
    assert res.status_code == 200
    movies = res.json()
    assert len(movies) == 10
    assert all(movie["rating_count"] >= 100 for movie in movies)
    assert res.headers["X-Recommendation-Mode"] == "cold-start"


def test_recommendations_for_unknown_genre_returns_empty_list(client, auth_headers):
    headers = auth_headers
    add_preferences(headers)
    res = client.get(
        "/api/v1/recommendations?genre_id=Western", headers=headers
    )
    assert res.status_code == 200
    assert res.json() == []


def test_tc14_more_than_ten_qualifying_movies_returns_exactly_ten(
    client, auth_headers
):
    headers = auth_headers
    # The fixture has 12 candidates; one watched movie still leaves 11.
    add_preferences(headers, ratings=4, watched=1)
    res = client.get(
        "/api/v1/recommendations", headers=headers
    )
    assert res.status_code == 200
    assert len(res.json()) == 10  # BR3


def test_tc15_personalized_rating_boundary_excludes_5_9_and_keeps_6_0(
    client, auth_headers
):
    headers = auth_headers
    add_preferences(headers)
    conn = auth.get_conn()
    conn.execute("UPDATE movie SET rating = 5.9 WHERE title = 'The Conjuring'")
    conn.execute("UPDATE movie SET rating = 6.0 WHERE title = 'Get Out'")
    conn.commit()
    conn.close()
    res = client.get(
        "/api/v1/recommendations?genre_id=Horror", headers=headers
    )
    assert res.status_code == 200
    titles = {movie["title"] for movie in res.json()}
    assert "The Conjuring" not in titles
    assert "Get Out" in titles


def test_rating_can_be_changed_without_creating_a_duplicate(client, auth_headers):
    headers = auth_headers

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


def test_rating_outside_one_to_ten_returns_clear_validation_message(client, auth_headers):
    res = client.post(
        "/api/v1/ratings", headers=auth_headers,
        json={"movie_id": 1, "score": 11},
    )

    assert res.status_code == 400
    assert res.json()["detail"] == "Rating must be between 1 and 10."


def test_marking_movie_watched_excludes_it_from_recommendations(client, auth_headers):
    headers = auth_headers
    add_preferences(headers, ratings=5)

    watched = client.post("/api/v1/movies/1/watch", headers=headers)
    movie = client.get("/api/v1/movies/1", headers=headers).json()
    recommendations = client.get("/api/v1/recommendations", headers=headers)

    assert watched.status_code == 200
    assert movie["watched"] == 1
    assert recommendations.status_code == 200
    assert 1 not in {item["id"] for item in recommendations.json()}


def test_tc08_four_preferences_still_uses_cold_start(client, auth_headers):
    headers = auth_headers
    add_preferences(headers, ratings=3, watched=1)

    res = client.get("/api/v1/recommendations", headers=headers)

    assert res.status_code == 200
    movies = res.json()
    assert len(movies) == 10
    assert all(movie["rating_count"] >= 100 for movie in movies)
    assert all(movie["imdb_id"].startswith("tt") for movie in movies)
    assert res.headers["X-Recommendation-Mode"] == "cold-start"


def test_tc12_exactly_five_preferences_uses_personalized_path(
    client, auth_headers
):
    headers = auth_headers
    add_preferences(headers, ratings=4, watched=1)

    res = client.get("/api/v1/recommendations", headers=headers)

    assert res.status_code == 200
    assert res.headers["X-Recommendation-Mode"] == "personalized"
    assert len(res.json()) <= 10


def test_tc11_fewer_than_ten_qualified_movies_returns_unavailable(
    client, auth_headers
):
    conn = auth.get_conn()
    conn.execute("UPDATE movie SET rating_count = 99")
    conn.commit()
    conn.close()

    res = client.get("/api/v1/recommendations", headers=auth_headers)

    assert res.status_code == 503
    assert res.json()["detail"]["code"] == "COLD_START_UNAVAILABLE"


def test_tc09_movie_with_99_votes_is_excluded_from_cold_start(
    client, auth_headers
):
    conn = auth.get_conn()
    conn.execute("UPDATE movie SET rating_count = 99 WHERE title = 'Parasite'")
    conn.commit()
    conn.close()

    res = client.get("/api/v1/recommendations", headers=auth_headers)

    assert res.status_code == 200
    assert len(res.json()) == 10
    assert "Parasite" not in [movie["title"] for movie in res.json()]


def test_cold_start_ignores_genre_filter(client, auth_headers):
    res = client.get("/api/v1/recommendations?genre_id=Horror", headers=auth_headers)
    assert res.status_code == 200
    assert res.headers["X-Recommendation-Mode"] == "cold-start"
    assert len(res.json()) == 10


def test_tc10_movie_with_exactly_100_votes_is_in_cold_start(client, auth_headers):
    conn = auth.get_conn()
    conn.execute("UPDATE movie SET rating_count = 100 WHERE title = 'Inception'")
    conn.commit()
    conn.close()
    res = client.get("/api/v1/recommendations", headers=auth_headers)
    assert "Inception" in [m["title"] for m in res.json()]  # BR8 boundary


def test_cold_start_is_sorted_by_rating_then_vote_count(client, auth_headers):
    res = client.get("/api/v1/recommendations", headers=auth_headers)
    ratings = [m["rating"] for m in res.json()]
    assert ratings == sorted(ratings, reverse=True)


def test_marking_movie_watched_twice_is_idempotent(client, auth_headers):
    headers = auth_headers
    assert client.post("/api/v1/movies/1/watch", headers=headers).status_code == 200
    assert client.post("/api/v1/movies/1/watch", headers=headers).status_code == 200


def test_watch_unknown_movie_returns_404(client, auth_headers):
    res = client.post("/api/v1/movies/999/watch", headers=auth_headers)
    assert res.status_code == 404


def test_rating_unknown_movie_returns_404(client, auth_headers):
    res = client.post("/api/v1/ratings", headers=auth_headers,
                      json={"movie_id": 999, "score": 5})
    assert res.status_code == 404


def test_rating_requires_token(client):
    res = client.post("/api/v1/ratings", json={"movie_id": 1, "score": 5})
    assert res.status_code == 401


def test_watched_movies_never_reappear_even_after_many_are_watched(client, auth_headers):
    headers = auth_headers
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



def test_tc13_highly_rated_horror_genre_is_recommended_first(
    client, auth_headers
):
    headers = auth_headers
    pid = int(headers["X-Profile-Id"])
    conn = auth.get_conn()
    # 5 ratings: Horror movies rated high, Romance rated low
    conn.executemany(
        "INSERT INTO rating (profile_id, movie_id, score) VALUES (?, ?, ?)",
        [(pid, 5, 10), (pid, 6, 10), (pid, 7, 9), (pid, 2, 3), (pid, 4, 2)],
    )
    conn.commit()
    conn.close()
    res = client.get("/api/v1/recommendations", headers=headers)
    genres = [m["genre"] for m in res.json()]
    assert res.headers["X-Recommendation-Mode"] == "personalized"
    assert genres[0] == "Horror"