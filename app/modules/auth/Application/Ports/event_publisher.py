"""
Application port for publishing auth events.
"""

from typing import Protocol

from app.modules.auth.Domain.Events import AuthEvent


class EventPublisherPort(Protocol):
    def dispatch(self, event: AuthEvent) -> None: ...
