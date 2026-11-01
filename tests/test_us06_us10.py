"""Tests for US10 (select a profile) and US06 (choose a genre): TC-01 to TC-06."""

import auth


def _login(client, email, password):
    return client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    )


def _stranger_profile_id():
    conn = auth.get_conn()
    try:
        return conn.execute(
            "SELECT id FROM profile WHERE name = 'Stranger'"
        ).fetchone()["id"]
    finally:
        conn.close()


# --- US10: select a profile before watching ---------------------------------


def test_tc01_login_returns_token_and_both_profiles(client):  # normal
    res = _login(client, auth.TEST_EMAIL, auth.TEST_PASSWORD)
    assert res.status_code == 200
    body = res.json()
    assert body["access_token"]
    assert [p["name"] for p in body["profiles"]] == ["Alex", "Sam"]


def test_tc02_wrong_password_is_rejected_with_401(client):  # error
    res = _login(client, auth.TEST_EMAIL, "wrong-password")
    assert res.status_code == 401
    assert "access_token" not in res.json()


def test_tc03_selecting_a_profile_of_another_account_returns_404(
    client, auth_headers
):  # error, BR10
    res = client.post(
        "/api/v1/profiles/select",
        json={"profile_id": _stranger_profile_id()},
        headers={"Authorization": auth_headers["Authorization"]},
    )
    assert res.status_code == 404


# --- US06: choose a theme before recommendations ----------------------------


def test_tc04_genre_list_has_each_genre_once(client, auth_headers):  # normal
    res = client.get("/api/v1/recommendations/setup/genres", headers=auth_headers)
    assert res.status_code == 200
    assert sorted(g["id"] for g in res.json()) == ["Horror", "Romance", "Thriller"]


def test_tc05_genre_list_without_profile_header_returns_400(
    client, auth_headers
):  # error
    res = client.get(
        "/api/v1/recommendations/setup/genres",
        headers={"Authorization": auth_headers["Authorization"]},
    )
    assert res.status_code == 400


def test_tc06_one_profiles_ratings_do_not_change_another_profiles_list(
    client, auth_headers
):  # normal, BR10 isolation
    alex = auth_headers
    token = {"Authorization": alex["Authorization"]}
    sam_id = client.get("/api/v1/profiles", headers=token).json()[1]["id"]
    sam = {**token, "X-Profile-Id": str(sam_id)}

    for movie_id in range(1, 6):  # Alex rates 5 movies through the API
        res = client.post(
            "/api/v1/ratings", headers=alex, json={"movie_id": movie_id, "score": 8}
        )
        assert res.status_code == 201

    alex_list = client.get("/api/v1/recommendations", headers=alex)
    sam_list = client.get("/api/v1/recommendations", headers=sam)

    assert alex_list.headers["X-Recommendation-Mode"] == "personalized"
    assert sam_list.headers["X-Recommendation-Mode"] == "cold-start"
    assert 3 in {m["id"] for m in sam_list.json()}  # Parasite, rated only by Alex