"""
Controller layer for auth HTTP orchestration.
"""

from sqlalchemy.orm import Session

from app.models.user import User
from app.modules.auth.Schemas.user import UserLogin, UserRegister
from app.modules.auth.Services import authService


class AuthController:
    def __init__(self) -> None:
        self.auth_service = authService

    def register(self, user: UserRegister, db: Session):
        return self.auth_service.register(user, db)

    def login(self, user: UserLogin, db: Session):
        return self.auth_service.login(user, db)

    def refresh(self, refresh_token: str, db: Session):
        return self.auth_service.refresh(refresh_token, db)

    def logout(self, refresh_token: str, db: Session):
        return self.auth_service.logout(refresh_token, db)

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
