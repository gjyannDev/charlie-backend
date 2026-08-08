"""
Domain events emitted by auth use-cases.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(slots=True)
class AuthEvent:
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(slots=True)
class UserRegistered(AuthEvent):
    user_id: int = 0
    email: str = ""
    role: str = ""


@dataclass(slots=True)
class UserLoggedIn(AuthEvent):
    user_id: int = 0
    email: str = ""


@dataclass(slots=True)
class TokenRefreshed(AuthEvent):
    user_id: int = 0
    email: str = ""


@dataclass(slots=True)
class UserLoggedOut(AuthEvent):
    user_id: int = 0
    token_id: int = 0
