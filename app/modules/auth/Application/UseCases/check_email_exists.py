"""
Check whether an auth email exists.
"""

from typing import Any

from app.modules.auth.Application.DTOs.auth_result import AuthUseCaseResult
from app.modules.auth.Application.Ports.user_repository import UserRepositoryPort
from app.modules.auth.Interfaces.HTTP.schemas import EmailCheckRequest


class CheckEmailExistsUseCase:
    def __init__(self, user_repository: UserRepositoryPort) -> None:
        self.user_repository = user_repository

    def execute(
        self, email_check: EmailCheckRequest, db: Any
    ) -> AuthUseCaseResult[dict[str, bool]]:
        db_user = self.user_repository.get_by_email(db, email_check.email)

        return AuthUseCaseResult({"exists": db_user is not None}, ())
