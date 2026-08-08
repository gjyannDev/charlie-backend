"""
Internal auth event listeners.
"""

from app.core.logging_config import get_logger
from app.modules.auth.Domain.Events import (
    TokenRefreshed,
    UserLoggedIn,
    UserLoggedOut,
    UserRegistered,
)


class AuthEventListener:
    def __init__(self) -> None:
        self.logger = get_logger(__name__)

    def handle_user_registered(self, event: UserRegistered) -> None:
        self.logger.info(
            "auth.event=user_registered user_id=%s email=%s role=%s",
            event.user_id,
            event.email,
            event.role,
        )

    def handle_user_logged_in(self, event: UserLoggedIn) -> None:
        self.logger.info(
            "auth.event=user_logged_in user_id=%s email=%s", event.user_id, event.email
        )

    def handle_token_refreshed(self, event: TokenRefreshed) -> None:
        self.logger.info(
            "auth.event=token_refreshed user_id=%s email=%s", event.user_id, event.email
        )

    def handle_user_logged_out(self, event: UserLoggedOut) -> None:
        self.logger.info(
            "auth.event=user_logged_out user_id=%s token_id=%s",
            event.user_id,
            event.token_id,
        )


authEventListener = AuthEventListener()
