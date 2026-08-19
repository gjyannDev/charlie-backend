"""
Refresh-access-token use case.
"""

from datetime import timedelta
from typing import Any

from app.modules.auth.Application.DTOs.auth_result import AuthUseCaseResult
from app.modules.auth.Application.Errors.auth_errors import (
    InvalidRefreshTokenError,
    InvalidUserStateError,
    UserInactiveError,
    UserNotFoundError,
)
from app.modules.auth.Application.Ports.refresh_token_repository import (
    RefreshTokenRepositoryPort,
)
from app.modules.auth.Application.Ports.token_issuer import TokenIssuerPort
from app.modules.auth.Application.Ports.unit_of_work import UnitOfWorkPort
from app.modules.auth.Application.Ports.user_repository import UserRepositoryPort
from app.modules.auth.Domain.Events import TokenRefreshed


class RefreshAccessTokenUseCase:
    def __init__(
        self,
        user_repository: UserRepositoryPort,
        token_issuer: TokenIssuerPort,
        refresh_token_repository: RefreshTokenRepositoryPort,
        unit_of_work: UnitOfWorkPort,
        access_token_expire_minutes: int,
        refresh_token_expire_minutes: int,
    ) -> None:
        self.user_repository = user_repository
        self.token_issuer = token_issuer
        self.refresh_token_repository = refresh_token_repository
        self.unit_of_work = unit_of_work
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_minutes = refresh_token_expire_minutes

    def execute(self, refresh_token: str, db: Any) -> AuthUseCaseResult[dict[str, str]]:
        payload = self.token_issuer.verify_refresh_token(refresh_token, db)
        user_id = payload["user_id"]
        email = payload["email"]

        db_token = self.refresh_token_repository.get_by_token(db, refresh_token)
        if not db_token:
            raise InvalidRefreshTokenError()

        db_user = self.user_repository.get_by_id(db, int(user_id))
        if not db_user:
            raise UserNotFoundError()
        db_user_id = db_user.id
        if db_user_id is None:
            raise InvalidUserStateError()
        if not db_user.is_active:
            raise UserInactiveError()

        access_expires = timedelta(minutes=self.access_token_expire_minutes)
        refresh_expires = timedelta(minutes=self.refresh_token_expire_minutes)
        new_access_token = self.token_issuer.create_access_token(
            user_email=email,
            user_id=db_user_id,
            role=db_user.role.value,
            expires_delta=access_expires,
        )
        new_refresh_token = self.token_issuer.create_refresh_token(
            user_email=email,
            user_id=db_user_id,
            expires_delta=refresh_expires,
        )

        self.refresh_token_repository.revoke(db, db_token)
        self.token_issuer.store_refresh_token(
            db,
            token=new_refresh_token,
            user_id=db_user_id,
            expires_delta=refresh_expires,
        )
        self.unit_of_work.commit(db)

        return AuthUseCaseResult(
            {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer",
            },
            (TokenRefreshed(user_id=db_user_id, email=db_user.email),),
        )
