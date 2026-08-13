"""
Application-level auth errors.
"""


class AuthApplicationError(Exception):
    default_detail = "Authentication error"

    def __init__(self, detail: str | None = None) -> None:
        self.detail = detail or self.default_detail
        super().__init__(self.detail)


class EmailAlreadyRegisteredError(AuthApplicationError):
    default_detail = "Email already registered"


class InvalidCredentialsError(AuthApplicationError):
    default_detail = "Invalid credentials"


class InvalidRoleError(AuthApplicationError):
    default_detail = "Invalid role"


class InvalidRefreshTokenError(AuthApplicationError):
    default_detail = "Invalid refresh token"


class RefreshTokenRevokedError(AuthApplicationError):
    default_detail = "Refresh token revoked"


class TokenExpiredError(AuthApplicationError):
    default_detail = "Token expired"


class UserNotFoundError(AuthApplicationError):
    default_detail = "User not found"


class InvalidUserStateError(AuthApplicationError):
    default_detail = "User record is invalid"
