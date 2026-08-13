"""
Application service facade for auth use cases.
"""

from typing import Any

from app.modules.auth.Application.Ports.event_publisher import EventPublisherPort
from app.modules.auth.Application.UseCases import (
    BuildRoleMessageUseCase,
    GetCurrentProfileUseCase,
    LoginUserUseCase,
    LogoutUserUseCase,
    RefreshAccessTokenUseCase,
    RegisterUserUseCase,
)
from app.modules.auth.Domain.Events import AuthEvent
from app.modules.auth.Interfaces.HTTP.schemas import UserLogin, UserRegister


class AuthApplicationService:
    def __init__(
        self,
        register_user: RegisterUserUseCase,
        login_user: LoginUserUseCase,
        refresh_access_token: RefreshAccessTokenUseCase,
        logout_user: LogoutUserUseCase,
        get_current_profile: GetCurrentProfileUseCase,
        build_role_message_use_case: BuildRoleMessageUseCase,
        event_publisher: EventPublisherPort,
    ) -> None:
        self.register_user = register_user
        self.login_user = login_user
        self.refresh_access_token = refresh_access_token
        self.logout_user = logout_user
        self.get_current_profile = get_current_profile
        self.build_role_message_use_case = build_role_message_use_case
        self.event_publisher = event_publisher

    def _publish_events(self, events: tuple[AuthEvent, ...]) -> None:
        for event in events:
            self.event_publisher.dispatch(event)

    def register(self, user: UserRegister, db: Any) -> Any:
        result = self.register_user.execute(user, db)
        self._publish_events(result.events)
        return result.value

    def login(self, user: UserLogin, db: Any) -> dict[str, str]:
        result = self.login_user.execute(user, db)
        self._publish_events(result.events)
        return result.value

    def refresh(self, refresh_token: str, db: Any) -> dict[str, str | None]:
        result = self.refresh_access_token.execute(refresh_token, db)
        self._publish_events(result.events)
        return result.value

    def logout(self, refresh_token: str, db: Any) -> dict[str, str]:
        result = self.logout_user.execute(refresh_token, db)
        self._publish_events(result.events)
        return result.value

    def get_me(self, current_user: Any) -> Any:
        return self.get_current_profile.execute(current_user)

    def build_role_message(self, message: str, current_user: Any) -> dict[str, str]:
        return self.build_role_message_use_case.execute(message, current_user)
