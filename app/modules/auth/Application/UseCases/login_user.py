"""
Login use case.
"""

from datetime import timedelta
from typing import Any

from app.modules.auth.Application.DTOs.auth_result import AuthUseCaseResult
from app.modules.auth.Application.Errors.auth_errors import (
    InvalidCredentialsError,
    InvalidUserStateError,
)
from app.modules.auth.Application.Ports.password_hasher import PasswordHasherPort
from app.modules.auth.Application.Ports.token_issuer import TokenIssuerPort
from app.modules.auth.Application.Ports.unit_of_work import UnitOfWorkPort
from app.modules.auth.Application.Ports.user_repository import UserRepositoryPort
from app.modules.auth.Domain.Events import UserLoggedIn
from app.modules.auth.Interfaces.HTTP.schemas import UserLogin


class LoginUserUseCase:
    def __init__(
        self,
        user_repository: UserRepositoryPort,
        password_hasher: PasswordHasherPort,
        token_issuer: TokenIssuerPort,
        unit_of_work: UnitOfWorkPort,
        access_token_expire_minutes: int,
        refresh_token_expire_minutes: int,
    ) -> None:
        self.user_repository = user_repository
        self.password_hasher = password_hasher
        self.token_issuer = token_issuer
        self.unit_of_work = unit_of_work
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_minutes = refresh_token_expire_minutes

    def execute(self, user: UserLogin, db: Any) -> AuthUseCaseResult[dict[str, str]]:
        db_user = self.user_repository.get_by_email(db, user.email)
        if not db_user or not self.password_hasher.verify(
            user.password, db_user.hashed_password
        ):
            raise InvalidCredentialsError()

        db_user_id = db_user.id
        if db_user_id is None:
            raise InvalidUserStateError()

        access_expires = timedelta(minutes=self.access_token_expire_minutes)
        refresh_expires = timedelta(minutes=self.refresh_token_expire_minutes)
        access_token = self.token_issuer.create_access_token(
            user_email=db_user.email,
            user_id=db_user_id,
            role=db_user.role.value,
            expires_delta=access_expires,
        )
        refresh_token = self.token_issuer.create_refresh_token(
            user_email=db_user.email,
            user_id=db_user_id,
            expires_delta=refresh_expires,
        )

        self.token_issuer.store_refresh_token(
            db,
            token=refresh_token,
            user_id=db_user_id,
            expires_delta=refresh_expires,
        )
        self.unit_of_work.commit(db)

        return AuthUseCaseResult(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            },
            (UserLoggedIn(user_id=db_user_id, email=db_user.email),),
        )
