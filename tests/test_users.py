def test_users_prefix_is_not_registered(client):
    response = client.get("/users/me")
    assert response.status_code == 404
