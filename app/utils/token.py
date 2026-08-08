"""
Compatibility wrappers for legacy token imports.
"""

from sqlalchemy.orm import Session

from app.models.user import User
from app.modules.auth.Services import get_current_user, oauth2_scheme, tokenService


def create_access_token(*args, **kwargs) -> str:
    return tokenService.create_access_token(*args, **kwargs)


def create_refresh_token(*args, **kwargs) -> str:
    return tokenService.create_refresh_token(*args, **kwargs)


def store_token(*args, **kwargs):
    return tokenService.store_token(*args, **kwargs)


def verify_token(token: str, db: Session, is_refresh: bool = False) -> dict:
    return tokenService.verify_token(token, db, is_refresh=is_refresh)


__all__ = [
    "User",
    "create_access_token",
    "create_refresh_token",
    "get_current_user",
    "oauth2_scheme",
    "store_token",
    "verify_token",
]
