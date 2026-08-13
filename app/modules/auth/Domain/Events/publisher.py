from collections.abc import Callable
from typing import Protocol

from .auth_events import AuthEvent

AuthEventHandler = Callable[..., None]


class AuthEventPublisher(Protocol):
    def dispatch(self, event: AuthEvent) -> None:
        """Publish an auth domain event to registered listeners."""
