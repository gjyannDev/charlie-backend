from app.modules.auth.Domain.Enums import UserRole
from app.modules.auth.Domain.Events import UserRegistered
from app.modules.auth.Domain.Rules import authRules
from app.modules.auth.Listeners import authEventDispatcher


def test_register_and_login_flow(client):
    register_response = client.post(
        "/auth/register",
        json={
            "email": "user@example.com",
            "full_name": "Example User",
            "password": "secret123",
            "role": "user",
        },
    )
    assert register_response.status_code == 200
    assert register_response.json()["email"] == "user@example.com"

    login_response = client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "secret123"},
    )
    assert login_response.status_code == 200
    payload = login_response.json()
    assert payload["access_token"]
    assert payload["refresh_token"]
    assert payload["token_type"] == "bearer"

    me_response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {payload['access_token']}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "user@example.com"


def test_refresh_and_logout_flow(client):
    client.post(
        "/auth/register",
        json={
            "email": "refresh@example.com",
            "full_name": "Refresh User",
            "password": "secret123",
            "role": "user",
        },
    )
    login_response = client.post(
        "/auth/login",
        json={"email": "refresh@example.com", "password": "secret123"},
    )
    refresh_token = login_response.json()["refresh_token"]

    refresh_response = client.post("/auth/refresh", params={"refresh_token": refresh_token})
    assert refresh_response.status_code == 200
    assert refresh_response.json()["access_token"]
    assert refresh_response.json()["refresh_token"] is None

    logout_response = client.post("/auth/logout", params={"refresh_token": refresh_token})
    assert logout_response.status_code == 200
    assert logout_response.json()["message"] == "Refresh token revoked successfully"


def test_admin_endpoint_requires_admin_role(client):
    client.post(
        "/auth/register",
        json={
            "email": "admin@example.com",
            "full_name": "Admin User",
            "password": "secret123",
            "role": "admin",
        },
    )
    admin_login = client.post(
        "/auth/login",
        json={"email": "admin@example.com", "password": "secret123"},
    )
    admin_token = admin_login.json()["access_token"]

    admin_response = client.get(
        "/auth/admin-role",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert admin_response.status_code == 200
    assert admin_response.json()["role"] == "admin"

    client.post(
        "/auth/register",
        json={
            "email": "plain@example.com",
            "full_name": "Plain User",
            "password": "secret123",
            "role": "user",
        },
    )
    user_login = client.post(
        "/auth/login",
        json={"email": "plain@example.com", "password": "secret123"},
    )
    user_token = user_login.json()["access_token"]

    denied_response = client.get(
        "/auth/admin-role",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert denied_response.status_code == 403


def test_users_routes_are_removed(client):
    response = client.post(
        "/users/register",
        json={
            "email": "old@example.com",
            "full_name": "Old User",
            "password": "secret123",
            "role": "user",
        },
    )
    assert response.status_code == 404


def test_auth_rules_accept_string_role():
    assert authRules.parse_user_role("admin") == UserRole.ADMIN


def test_auth_rules_reject_invalid_role():
    try:
        authRules.parse_user_role("owner")
    except ValueError as exc:
        assert str(exc) == "Invalid role"
    else:
        raise AssertionError("Expected ValueError for invalid role")


def test_auth_event_dispatcher_invokes_listener(monkeypatch):
    calls = []

    def fake_listener(event):
        calls.append(event.email)

    monkeypatch.setitem(
        authEventDispatcher.listeners,
        UserRegistered,
        (fake_listener,),
    )

    authEventDispatcher.dispatch(
        UserRegistered(user_id=1, email="event@example.com", role="user")
    )

    assert calls == ["event@example.com"]
