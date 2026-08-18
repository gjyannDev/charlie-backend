from datetime import UTC, datetime, timedelta

from fastapi import HTTPException

from app.models.user import Token
from app.modules.auth.Application.Errors.auth_errors import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    InvalidRoleError,
    InvalidUserStateError,
    RefreshTokenRevokedError,
    UserNotFoundError,
)
from app.modules.auth.Application.DTOs import AuthUseCaseResult
from app.modules.auth.Application.Services import AuthApplicationService
from app.modules.auth.Domain.Enums import UserRole
from app.modules.auth.Domain.Events import UserRegistered
from app.modules.auth.Domain.Policies import rolePolicy
from app.modules.auth.Infrastructure.Eventing import (
    AuthEventDispatcher,
    inProcessEventDispatcher,
)
from app.modules.auth.Interfaces.HTTP.auth_controller import AuthController
from app.modules.auth.Interfaces.HTTP.error_mapper import map_auth_error


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


def test_cors_allows_local_frontend_with_credentials(client):
    response = client.options(
        "/auth/check-email",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert response.headers["access-control-allow-credentials"] == "true"


def test_check_email_returns_true_for_existing_email(client):
    client.post(
        "/auth/register",
        json={
            "email": "known@example.com",
            "full_name": "Known User",
            "password": "secret123",
            "role": "user",
        },
    )

    response = client.post("/auth/check-email", json={"email": "known@example.com"})

    assert response.status_code == 200
    assert response.json() == {"exists": True}


def test_check_email_returns_false_for_missing_email(client):
    response = client.post("/auth/check-email", json={"email": "missing@example.com"})

    assert response.status_code == 200
    assert response.json() == {"exists": False}


def test_check_email_rejects_invalid_email(client):
    response = client.post("/auth/check-email", json={"email": "not-an-email"})

    assert response.status_code == 422


def test_check_email_does_not_require_authentication(client):
    response = client.post("/auth/check-email", json={"email": "public@example.com"})

    assert response.status_code == 200
    assert response.json() == {"exists": False}


def test_duplicate_register_maps_application_error_to_http(client):
    payload = {
        "email": "duplicate@example.com",
        "full_name": "Duplicate User",
        "password": "secret123",
        "role": "user",
    }

    first_response = client.post("/auth/register", json=payload)
    duplicate_response = client.post("/auth/register", json=payload)

    assert first_response.status_code == 200
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Email already registered"


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
    assert rolePolicy.parse_user_role("admin") == UserRole.ADMIN


def test_auth_rules_reject_invalid_role():
    try:
        rolePolicy.parse_user_role("owner")
    except ValueError as exc:
        assert str(exc) == "Invalid role"
    else:
        raise AssertionError("Expected ValueError for invalid role")


def test_auth_error_mapper_preserves_http_contract():
    cases = [
        (EmailAlreadyRegisteredError(), 400, "Email already registered"),
        (InvalidCredentialsError(), 400, "Invalid credentials"),
        (InvalidRoleError(), 400, "Invalid role"),
        (InvalidRefreshTokenError(), 400, "Invalid refresh token"),
        (RefreshTokenRevokedError(), 401, "Refresh token revoked"),
        (UserNotFoundError(), 401, "User not found"),
        (InvalidUserStateError(), 500, "User record is invalid"),
        (InvalidUserStateError("User creation failed"), 500, "User creation failed"),
    ]

    for error, status_code, detail in cases:
        http_error = map_auth_error(error)

        assert isinstance(http_error, HTTPException)
        assert http_error.status_code == status_code
        assert http_error.detail == detail


def test_auth_event_dispatcher_invokes_listener(monkeypatch):
    calls = []

    def fake_listener(event):
        calls.append(event.email)

    monkeypatch.setitem(
        inProcessEventDispatcher.listeners,
        UserRegistered,
        (fake_listener,),
    )

    inProcessEventDispatcher.dispatch(
        UserRegistered(user_id=1, email="event@example.com", role="user")
    )

    assert calls == ["event@example.com"]


def test_auth_event_dispatcher_supports_multiple_listeners():
    calls = []

    def first_listener(event):
        calls.append(("first", event.email))

    def second_listener(event):
        calls.append(("second", event.email))

    dispatcher = AuthEventDispatcher()
    dispatcher.register(UserRegistered, first_listener, second_listener)

    dispatcher.dispatch(
        UserRegistered(user_id=1, email="event@example.com", role="user")
    )

    assert calls == [
        ("first", "event@example.com"),
        ("second", "event@example.com"),
    ]


def test_auth_controller_delegates_to_application_service():
    expected_value = object()

    class FakeAuthService:
        def register(self, user, db):
            return expected_value

    controller = AuthController()
    controller.auth_service = FakeAuthService()

    result = controller.register(user=object(), db=object())

    assert result is expected_value


def test_auth_application_service_publishes_use_case_events():
    published = []
    expected_value = object()
    expected_event = UserRegistered(user_id=1, email="event@example.com", role="user")

    class FakeUseCase:
        def execute(self, *args):
            return AuthUseCaseResult(value=expected_value, events=(expected_event,))

    class FakeEventPublisher:
        def dispatch(self, event):
            published.append((type(event).__name__, event.email))

    service = AuthApplicationService(
        register_user=FakeUseCase(),
        login_user=FakeUseCase(),
        refresh_access_token=FakeUseCase(),
        logout_user=FakeUseCase(),
        get_current_profile=FakeUseCase(),
        build_role_message_use_case=FakeUseCase(),
        check_email_exists=FakeUseCase(),
        event_publisher=FakeEventPublisher(),
    )

    result = service.register(user=object(), db=object())

    assert result is expected_value
    assert published == [("UserRegistered", "event@example.com")]


def test_auth_application_service_does_not_publish_events_on_failure():
    published = []

    class FailingUseCase:
        def execute(self, *args):
            raise EmailAlreadyRegisteredError()

    class UnusedUseCase:
        def execute(self, *args):
            raise AssertionError("Unexpected use case call")

    class FakeEventPublisher:
        def dispatch(self, event):
            published.append(event)

    service = AuthApplicationService(
        register_user=FailingUseCase(),
        login_user=UnusedUseCase(),
        refresh_access_token=UnusedUseCase(),
        logout_user=UnusedUseCase(),
        get_current_profile=UnusedUseCase(),
        build_role_message_use_case=UnusedUseCase(),
        check_email_exists=UnusedUseCase(),
        event_publisher=FakeEventPublisher(),
    )

    try:
        service.register(user=object(), db=object())
    except EmailAlreadyRegisteredError:
        pass
    else:
        raise AssertionError("Expected EmailAlreadyRegisteredError")

    assert published == []
