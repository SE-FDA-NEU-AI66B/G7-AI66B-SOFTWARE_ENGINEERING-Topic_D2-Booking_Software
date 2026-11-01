"""Tests for rating a movie and marking it as watched (TC-16 to TC-24).

Business rule BR1: a movie the profile has watched (or rated, which also marks
it watched) is never recommended again.
"""

import auth

RATINGS_URL = "/api/v1/ratings"
RECOMMENDATIONS_URL = "/api/v1/recommendations"
UNKNOWN_MOVIE_ID = 9999


def _profile_id(headers):
    return int(headers["X-Profile-Id"])


def _count(table, headers, movie_id=None):
    """Count rows in `table` for the profile (optionally for a single movie)."""
    sql = f"SELECT COUNT(*) FROM {table} WHERE profile_id = ?"
    params = [_profile_id(headers)]
    if movie_id is not None:
        sql += " AND movie_id = ?"
        params.append(movie_id)
    conn = auth.get_conn()
    try:
        return conn.execute(sql, params).fetchone()[0]
    finally:
        conn.close()


def _recommended_ids(client, headers, genre_id=None):
    url = RECOMMENDATIONS_URL + (f"?genre_id={genre_id}" if genre_id else "")
    res = client.get(url, headers=headers)
    assert res.status_code == 200
    return [movie["id"] for movie in res.json()]


# --------------------------------------------------------------------------
# TC-16 / TC-17 / TC-18: score boundaries
# --------------------------------------------------------------------------


def test_tc16_boundary_score_1_is_accepted(client, auth_headers):
    # TC-16
    res = client.post(
        RATINGS_URL, headers=auth_headers, json={"movie_id": 1, "score": 1}
    )

    assert res.status_code == 201
    assert res.json() == {"movie_id": 1, "score": 1}
    assert _count("rating", auth_headers, movie_id=1) == 1


def test_tc17_boundary_score_10_is_accepted(client, auth_headers):
    # TC-17
    res = client.post(
        RATINGS_URL, headers=auth_headers, json={"movie_id": 1, "score": 10}
    )

    assert res.status_code == 201
    assert res.json() == {"movie_id": 1, "score": 10}
    assert _count("rating", auth_headers, movie_id=1) == 1


def test_tc18_boundary_score_0_and_11_are_rejected_and_nothing_is_saved(
    client, auth_headers
):
    # TC-18
    for bad_score in (0, 11):
        res = client.post(
            RATINGS_URL,
            headers=auth_headers,
            json={"movie_id": 1, "score": bad_score},
        )

        assert res.status_code == 400, f"score {bad_score}"
        assert res.json()["detail"] == "Rating must be between 1 and 10."

    assert _count("rating", auth_headers) == 0
    assert _count("watch_history", auth_headers) == 0


# --------------------------------------------------------------------------
# TC-19 / TC-20: overwrite and error cases for ratings
# --------------------------------------------------------------------------


def test_tc19_rating_same_movie_again_overwrites_score_and_keeps_one_row(
    client, auth_headers
):
    # TC-19
    first = client.post(
        RATINGS_URL, headers=auth_headers, json={"movie_id": 1, "score": 4}
    )
    second = client.post(
        RATINGS_URL, headers=auth_headers, json={"movie_id": 1, "score": 9}
    )

    assert first.status_code == 201
    assert second.status_code == 201
    assert _count("rating", auth_headers, movie_id=1) == 1
    conn = auth.get_conn()
    try:
        score = conn.execute(
            "SELECT score FROM rating WHERE profile_id = ? AND movie_id = 1",
            (_profile_id(auth_headers),),
        ).fetchone()[0]
    finally:
        conn.close()
    assert score == 9


def test_tc20_rating_unknown_movie_returns_404_and_nothing_is_saved(
    client, auth_headers
):
    # TC-20 (unknown movie id)
    res = client.post(
        RATINGS_URL,
        headers=auth_headers,
        json={"movie_id": UNKNOWN_MOVIE_ID, "score": 7},
    )

    assert res.status_code == 404
    assert _count("rating", auth_headers) == 0
    assert _count("watch_history", auth_headers) == 0


def test_tc20_rating_without_token_returns_401(client):
    # TC-20 (missing token)
    res = client.post(RATINGS_URL, json={"movie_id": 1, "score": 7})

    assert res.status_code == 401


# --------------------------------------------------------------------------
# TC-21 / TC-22 / TC-23: watched movies are not recommended (BR1)
# --------------------------------------------------------------------------


def test_tc21_marking_movie_watched_removes_it_from_next_recommendations(
    client, auth_headers
):
    # TC-21
    before = _recommended_ids(client, auth_headers)
    target = before[0]  # a movie that is currently recommended

    res = client.post(f"/api/v1/movies/{target}/watch", headers=auth_headers)

    assert res.status_code == 200
    after = _recommended_ids(client, auth_headers)
    assert target not in after


def test_tc22_rating_a_movie_also_marks_it_watched_so_it_is_not_recommended(
    client, auth_headers
):
    # TC-22 (BR1)
    before = _recommended_ids(client, auth_headers)
    target = before[0]

    res = client.post(
        RATINGS_URL, headers=auth_headers, json={"movie_id": target, "score": 8}
    )

    assert res.status_code == 201
    assert _count("watch_history", auth_headers, movie_id=target) == 1
    after = _recommended_ids(client, auth_headers)
    assert target not in after


def test_tc23_boundary_25_watched_movies_never_reappear(client, auth_headers):
    # TC-23: the extra movies are inserted here, the real seed file is not used.
    # The 25 watched movies get the best rating, so they would dominate the top
    # 10 if the watch_history exclusion were missing.
    extra_ids = list(range(100, 125))
    conn = auth.get_conn()
    try:
        conn.executemany(
            "INSERT INTO movie (id, title, genre, rating, rating_count, imdb_id) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            [
                (movie_id, f"Extra {movie_id}", "Thriller", 9.9, 500000, f"tt9{movie_id}")
                for movie_id in extra_ids
            ],
        )
        conn.commit()
    finally:
        conn.close()

    for movie_id in extra_ids:
        res = client.post(f"/api/v1/movies/{movie_id}/watch", headers=auth_headers)
        assert res.status_code == 200

    assert _count("watch_history", auth_headers) == 25

    # No genre filter: 12 unwatched movies remain, so the list is full (10).
    recommended = _recommended_ids(client, auth_headers)
    assert len(recommended) == 10
    assert not set(recommended) & set(extra_ids)

    # Thriller only: the 25 extras are all watched, so just the 5 original
    # Thriller movies (ids 1, 3, 9, 11, 12) can be recommended.
    thrillers = _recommended_ids(client, auth_headers, "Thriller")
    assert set(thrillers) == {1, 3, 9, 11, 12}


# --------------------------------------------------------------------------
# TC-24: marking watched twice / unknown movie
# --------------------------------------------------------------------------


def test_tc24_marking_same_movie_watched_twice_is_harmless(client, auth_headers):
    # TC-24 (repeat call)
    first = client.post("/api/v1/movies/1/watch", headers=auth_headers)
    second = client.post("/api/v1/movies/1/watch", headers=auth_headers)

    assert first.status_code == 200
    assert second.status_code == 200
    assert _count("watch_history", auth_headers, movie_id=1) == 1


def test_tc24_marking_unknown_movie_watched_returns_404(client, auth_headers):
    # TC-24 (unknown movie id)
    res = client.post(
        f"/api/v1/movies/{UNKNOWN_MOVIE_ID}/watch", headers=auth_headers
    )

    assert res.status_code == 404
    assert _count("watch_history", auth_headers) == 0