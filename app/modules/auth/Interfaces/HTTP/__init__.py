from .schemas import (
    EmailCheckRequest,
    EmailCheckResponse,
    MeSchema,
    RefreshTokenRequest,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)

__all__ = [
    "AuthController",
    "EmailCheckRequest",
    "EmailCheckResponse",
    "MeSchema",
    "RefreshTokenRequest",
    "TokenResponse",
    "UserLogin",
    "UserRegister",
    "UserResponse",
    "authController",
    "auth_router",
    "get_current_user",
    "oauth2_scheme",
]


def __getattr__(name: str):
    if name in {"get_current_user", "oauth2_scheme"}:
        from .auth_dependencies import get_current_user, oauth2_scheme

        return {
            "get_current_user": get_current_user,
            "oauth2_scheme": oauth2_scheme,
        }[name]

    if name == "auth_router":
        from .auth_routes import auth_router

        return auth_router

    if name in {"AuthController", "authController"}:
        from .auth_controller import AuthController, authController

        return {
            "AuthController": AuthController,
            "authController": authController,
        }[name]

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
