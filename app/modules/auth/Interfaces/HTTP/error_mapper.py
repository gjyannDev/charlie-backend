"""
HTTP mapping for auth application errors.
"""

from fastapi import HTTPException

from app.modules.auth.Application.Errors.auth_errors import (
    AuthApplicationError,
    EmailAlreadyRegisteredError,
    EmailNotFoundError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    InvalidRoleError,
    InvalidUserStateError,
    RefreshTokenRevokedError,
    TokenExpiredError,
    UserInactiveError,
    UserNotFoundError,
)

_AUTH_ERROR_STATUS: dict[type[AuthApplicationError], int] = {
    EmailAlreadyRegisteredError: 400,
    EmailNotFoundError: 404,
    InvalidCredentialsError: 400,
    InvalidRoleError: 400,
    InvalidRefreshTokenError: 400,
    RefreshTokenRevokedError: 401,
    TokenExpiredError: 498,
    UserInactiveError: 403,
    UserNotFoundError: 401,
    InvalidUserStateError: 500,
}


def map_auth_error(error: AuthApplicationError) -> HTTPException:
    return HTTPException(
        status_code=_AUTH_ERROR_STATUS[type(error)],
        detail=error.detail,
    )
