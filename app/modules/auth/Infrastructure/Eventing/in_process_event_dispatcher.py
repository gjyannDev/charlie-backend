"""
Simple in-process dispatcher for auth domain events.
"""

from collections.abc import Mapping

from app.modules.auth.Domain.Events import (
    AuthEvent,
    AuthEventHandler,
    TokenRefreshed,
    UserLoggedIn,
    UserLoggedOut,
    UserRegistered,
)
from app.modules.auth.Infrastructure.Eventing.auth_event_listener import (
    authEventListener,
)


class AuthEventDispatcher:
    def __init__(
        self,
        listeners: Mapping[type[AuthEvent], tuple[AuthEventHandler, ...]] | None = None,
    ) -> None:
        self.listeners: dict[type[AuthEvent], tuple[AuthEventHandler, ...]] = (
            dict(listeners or {})
        )

    def dispatch(self, event: AuthEvent) -> None:
        for listener in self.listeners.get(type(event), ()):
            listener(event)

    def register(
        self, event_type: type[AuthEvent], *listeners: AuthEventHandler
    ) -> None:
        self.listeners[event_type] = self.listeners.get(event_type, ()) + listeners


inProcessEventDispatcher = AuthEventDispatcher(
    {
        UserRegistered: (authEventListener.handle_user_registered,),
        UserLoggedIn: (authEventListener.handle_user_logged_in,),
        TokenRefreshed: (authEventListener.handle_token_refreshed,),
        UserLoggedOut: (authEventListener.handle_user_logged_out,),
    }
)
