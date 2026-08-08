from datetime import UTC, datetime, timedelta

from app.models.user import Token
from app.modules.auth.Domain.Enums import UserRole
from app.modules.auth.Domain.Events import UserRegistered
from app.modules.auth.Domain.Rules import authRules
from app.modules.auth.Listeners import authEventDispatcher


def test_register_and_login_flow(client, db_session):
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

    token_rows = db_session.query(Token).all()
    assert len(token_rows) == 1
    assert token_rows[0].token == payload["refresh_token"]

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

    refresh_response = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_response.status_code == 200
    assert refresh_response.json()["access_token"]
    assert refresh_response.json()["refresh_token"] is None

    logout_response = client.post(
        "/auth/logout",
        json={"refresh_token": refresh_token},
    )
    assert logout_response.status_code == 200
    assert logout_response.json()["message"] == "Refresh token revoked successfully"

    post_logout_refresh = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert post_logout_refresh.status_code == 401


def test_refresh_token_expiry_is_enforced(client, db_session):
    client.post(
        "/auth/register",
        json={
            "email": "expired@example.com",
            "full_name": "Expired User",
            "password": "secret123",
            "role": "user",
        },
    )
    login_response = client.post(
        "/auth/login",
        json={"email": "expired@example.com", "password": "secret123"},
    )
    refresh_token = login_response.json()["refresh_token"]

    db_token = db_session.query(Token).filter(Token.token == refresh_token).one()
    db_token.expired_at = datetime.now(UTC) - timedelta(minutes=5)
    db_session.commit()

    expired_response = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert expired_response.status_code == 498


def test_refresh_and_logout_reject_query_params(client):
    refresh_response = client.post(
        "/auth/refresh",
        params={"refresh_token": "not-used"},
    )
    assert refresh_response.status_code == 422

    logout_response = client.post(
        "/auth/logout",
        params={"refresh_token": "not-used"},
    )
    assert logout_response.status_code == 422


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
