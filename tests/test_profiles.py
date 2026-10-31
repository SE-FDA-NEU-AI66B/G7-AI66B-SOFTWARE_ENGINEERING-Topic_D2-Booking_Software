import auth
def stranger_profile_id():
    conn = auth.get_conn()
    pid = conn.execute("SELECT id FROM profile WHERE name = 'Stranger'").fetchone()["id"]
    conn.close()
    return pid


def test_list_profiles_requires_token(client):
    assert client.get("/api/v1/profiles").status_code == 401


def test_list_profiles_returns_only_own_profiles(client, auth_headers):
    res = client.get("/api/v1/profiles", headers=auth_headers)
    assert res.status_code == 200
    assert [p["name"] for p in res.json()] == ["Alex", "Sam"]


def test_invalid_token_returns_401(client):
    res = client.get("/api/v1/profiles", headers={"Authorization": "Bearer nonsense"})
    assert res.status_code == 401


def test_select_own_profile_returns_200(client, auth_headers):
    own_id = client.get("/api/v1/profiles", headers=auth_headers).json()[0]["id"]
    res = client.post(
        "/api/v1/profiles/select", json={"profile_id": own_id}, headers=auth_headers
    )
    assert res.status_code == 200
    assert res.json()["name"] == "Alex"


def test_select_profile_of_another_account_returns_404(client, auth_headers):
    res = client.post(
        "/api/v1/profiles/select",
        json={"profile_id": stranger_profile_id()},
        headers=auth_headers,
    )
    assert res.status_code == 404


def test_select_without_profile_id_returns_400(client, auth_headers):
    res = client.post("/api/v1/profiles/select", json={}, headers=auth_headers)
    assert res.status_code == 400


def test_scoped_endpoint_needs_profile_header(client, auth_headers):
    headers = {"Authorization": auth_headers["Authorization"]}
    assert client.get("/api/v1/profiles/me", headers=headers).status_code == 400


def test_scoped_endpoint_rejects_profile_of_another_account(client, auth_headers):
    headers = {**auth_headers, "X-Profile-Id": str(stranger_profile_id())}
    assert client.get("/api/v1/profiles/me", headers=headers).status_code == 404


def test_scoped_endpoint_returns_selected_profile(client, auth_headers):
    sam_id = client.get("/api/v1/profiles", headers=auth_headers).json()[1]["id"]
    headers = {**auth_headers, "X-Profile-Id": str(sam_id)}
    res = client.get("/api/v1/profiles/me", headers=headers)
    assert res.status_code == 200
    assert res.json()["name"] == "Sam"