"""
Register-user use case.
"""

from typing import Any

from app.modules.auth.Application.DTOs.auth_result import AuthUseCaseResult
from app.modules.auth.Application.Errors.auth_errors import (
    EmailAlreadyRegisteredError,
    InvalidRoleError,
    InvalidUserStateError,
)
from app.modules.auth.Application.Ports.password_hasher import PasswordHasherPort
from app.modules.auth.Application.Ports.unit_of_work import UnitOfWorkPort
from app.modules.auth.Application.Ports.user_repository import UserRepositoryPort
from app.modules.auth.Domain.Events import UserRegistered
from app.modules.auth.Domain.Policies import RolePolicy
from app.modules.auth.Interfaces.HTTP.schemas import UserRegister


class RegisterUserUseCase:
    def __init__(
        self,
        user_repository: UserRepositoryPort,
        password_hasher: PasswordHasherPort,
        role_policy: RolePolicy,
        unit_of_work: UnitOfWorkPort,
    ) -> None:
        self.user_repository = user_repository
        self.password_hasher = password_hasher
        self.role_policy = role_policy
        self.unit_of_work = unit_of_work

    def execute(self, user: UserRegister, db: Any) -> AuthUseCaseResult[Any]:
        existing_user = self.user_repository.get_by_email(db, user.email)
        if existing_user:
            raise EmailAlreadyRegisteredError()

        try:
            role = self.role_policy.parse_user_role(user.role)
        except ValueError as exc:
            raise InvalidRoleError() from exc

        new_user = self.user_repository.create(
            db,
            email=user.email,
            full_name=user.full_name,
            role=role,
            hashed_password=self.password_hasher.hash(user.password),
        )
        if new_user.id is None:
            raise InvalidUserStateError("User creation failed")

        self.unit_of_work.commit(db)
        return AuthUseCaseResult(
            new_user,
            (
                UserRegistered(
                    user_id=new_user.id,
                    email=new_user.email,
                    role=new_user.role.value,
                ),
            ),
        )
