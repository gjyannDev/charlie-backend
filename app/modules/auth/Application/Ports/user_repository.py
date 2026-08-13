"""
Application port for user persistence.
"""

from typing import Any, Protocol

from app.modules.auth.Domain.Enums import UserRole


class UserRepositoryPort(Protocol):
    def get_by_email(self, db: Any, email: str) -> Any | None: ...

    def get_by_id(self, db: Any, user_id: int) -> Any | None: ...

    def create(
        self,
        db: Any,
        *,
        email: str,
        full_name: str,
        role: UserRole,
        hashed_password: str,
    ) -> Any: ...
