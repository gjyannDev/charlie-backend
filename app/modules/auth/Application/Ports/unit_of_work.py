"""
Application port for transaction ownership.
"""

from typing import Any, Protocol


class UnitOfWorkPort(Protocol):
    def commit(self, db: Any) -> None: ...
