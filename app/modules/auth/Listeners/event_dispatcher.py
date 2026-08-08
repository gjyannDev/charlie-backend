"""
Simple in-process dispatcher for auth domain events.
"""

from collections.abc import Callable

from app.modules.auth.Domain.Events import (
    AuthEvent,
    TokenRefreshed,
    UserLoggedIn,
    UserLoggedOut,
    UserRegistered,
)
from app.modules.auth.Listeners.auth_event_listener import authEventListener

AuthEventHandler = Callable[[AuthEvent], None]


class AuthEventDispatcher:
    def __init__(self) -> None:
        self.listeners: dict[type[AuthEvent], tuple[AuthEventHandler, ...]] = {
            UserRegistered: (authEventListener.handle_user_registered,),
            UserLoggedIn: (authEventListener.handle_user_logged_in,),
            TokenRefreshed: (authEventListener.handle_token_refreshed,),
            UserLoggedOut: (authEventListener.handle_user_logged_out,),
        }

    def dispatch(self, event: AuthEvent) -> None:
        for listener in self.listeners.get(type(event), ()):
            listener(event)


authEventDispatcher = AuthEventDispatcher()
