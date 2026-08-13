"""
Logout use case.
"""

from typing import Any

from app.modules.auth.Application.DTOs.auth_result import AuthUseCaseResult
from app.modules.auth.Application.Errors.auth_errors import InvalidRefreshTokenError
from app.modules.auth.Application.Ports.refresh_token_repository import (
    RefreshTokenRepositoryPort,
)
from app.modules.auth.Application.Ports.unit_of_work import UnitOfWorkPort
from app.modules.auth.Domain.Events import UserLoggedOut


class LogoutUserUseCase:
    def __init__(
        self,
        refresh_token_repository: RefreshTokenRepositoryPort,
        unit_of_work: UnitOfWorkPort,
    ) -> None:
        self.refresh_token_repository = refresh_token_repository
        self.unit_of_work = unit_of_work

    def execute(self, refresh_token: str, db: Any) -> AuthUseCaseResult[dict[str, str]]:
        db_token = self.refresh_token_repository.get_by_token(db, refresh_token)
        if not db_token:
            raise InvalidRefreshTokenError()

        self.refresh_token_repository.revoke(db, db_token)
        self.unit_of_work.commit(db)
        return AuthUseCaseResult(
            {"message": "Refresh token revoked successfully"},
            (UserLoggedOut(user_id=db_token.user_id, token_id=db_token.id),),
        )
