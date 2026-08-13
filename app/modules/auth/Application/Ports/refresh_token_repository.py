"""
Application port for refresh-token persistence.
"""

from datetime import datetime
from typing import Any, Protocol


class RefreshTokenRepositoryPort(Protocol):
    def create(
        self,
        db: Any,
        *,
        token: str,
        user_id: int,
        expired_at: datetime,
    ) -> Any: ...

    def get_by_token(self, db: Any, token: str) -> Any | None: ...

    def revoke(self, db: Any, db_token: Any) -> Any: ...
