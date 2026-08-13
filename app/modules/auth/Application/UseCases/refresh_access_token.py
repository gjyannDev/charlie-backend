"""
Refresh-access-token use case.
"""

from datetime import timedelta
from typing import Any

from app.modules.auth.Application.DTOs.auth_result import AuthUseCaseResult
from app.modules.auth.Application.Errors.auth_errors import (
    InvalidUserStateError,
    UserNotFoundError,
)
from app.modules.auth.Application.Ports.token_issuer import TokenIssuerPort
from app.modules.auth.Application.Ports.user_repository import UserRepositoryPort
from app.modules.auth.Domain.Events import TokenRefreshed


class RefreshAccessTokenUseCase:
    def __init__(
        self,
        user_repository: UserRepositoryPort,
        token_issuer: TokenIssuerPort,
        access_token_expire_minutes: int,
    ) -> None:
        self.user_repository = user_repository
        self.token_issuer = token_issuer
        self.access_token_expire_minutes = access_token_expire_minutes

    def execute(self, refresh_token: str, db: Any) -> AuthUseCaseResult[dict[str, str | None]]:
        payload = self.token_issuer.verify_refresh_token(refresh_token, db)
        user_id = payload["user_id"]
        email = payload["email"]

        db_user = self.user_repository.get_by_id(db, int(user_id))
        if not db_user:
            raise UserNotFoundError()
        db_user_id = db_user.id
        if db_user_id is None:
            raise InvalidUserStateError()

        access_expires = timedelta(minutes=self.access_token_expire_minutes)
        new_access_token = self.token_issuer.create_access_token(
            user_email=email,
            user_id=db_user_id,
            role=db_user.role.value,
            expires_delta=access_expires,
        )

        return AuthUseCaseResult(
            {
                "access_token": new_access_token,
                "refresh_token": None,
                "token_type": "bearer",
            },
            (TokenRefreshed(user_id=db_user_id, email=db_user.email),),
        )
