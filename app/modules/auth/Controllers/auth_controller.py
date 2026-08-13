"""
Controller layer for auth HTTP orchestration.
"""

from sqlalchemy.orm import Session

from app.models.user import User
from app.modules.auth.Domain.Events import AuthEvent
from app.modules.auth.Listeners import authEventDispatcher
from app.modules.auth.Schemas.user import UserLogin, UserRegister
from app.modules.auth.Services import authService


class AuthController:
    def __init__(self) -> None:
        self.auth_service = authService

    def _publish_events(self, events: tuple[AuthEvent, ...]) -> None:
        for event in events:
            authEventDispatcher.dispatch(event)

    def register(self, user: UserRegister, db: Session):
        result = self.auth_service.register(user, db)
        self._publish_events(result.events)
        return result.value

    def login(self, user: UserLogin, db: Session):
        result = self.auth_service.login(user, db)
        self._publish_events(result.events)
        return result.value

    def refresh(self, refresh_token: str, db: Session):
        result = self.auth_service.refresh(refresh_token, db)
        self._publish_events(result.events)
        return result.value

    def logout(self, refresh_token: str, db: Session):
        result = self.auth_service.logout(refresh_token, db)
        self._publish_events(result.events)
        return result.value

    def get_me(self, current_user: User):
        return self.auth_service.get_me(current_user)

    def admin_role(self, current_user: User):
        return self.auth_service.build_role_message(
            "This API is only accessible by the user who has the Admin role",
            current_user,
        )

    def user_role(self, current_user: User):
        return self.auth_service.build_role_message(
            "This API is only accessible by the user who has the User role",
            current_user,
        )

    def multi_role(self, current_user: User):
        return self.auth_service.build_role_message(
            "This API is only accessible by the user who has the User and Admin role",
            current_user,
        )


authController = AuthController()
