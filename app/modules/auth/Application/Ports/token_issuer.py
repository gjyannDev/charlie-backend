"""
Application port for issuing and validating tokens.
"""

from datetime import timedelta
from typing import Any, Mapping, Protocol


class TokenIssuerPort(Protocol):
    def create_access_token(
        self,
        user_email: str,
        user_id: int,
        expires_delta: timedelta | None = None,
        role: str | None = None,
        permissions: list[str] | None = None,
    ) -> str: ...

    def create_refresh_token(
        self,
        user_email: str,
        user_id: int,
        expires_delta: timedelta | None = None,
    ) -> str: ...

    def store_refresh_token(
        self,
        db: Any,
        token: str,
        user_id: int,
        expires_delta: timedelta,
    ) -> Any: ...

    def verify_refresh_token(self, token: str, db: Any) -> Mapping[str, Any]: ...
