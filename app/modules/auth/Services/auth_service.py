"""
Auth use-case services.
"""

from datetime import timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.modules.auth.Domain.Events import (
    TokenRefreshed,
    UserLoggedIn,
    UserLoggedOut,
    UserRegistered,
)
from app.modules.auth.Domain.Rules import authRules
from app.modules.auth.Listeners import authEventDispatcher
from app.modules.auth.Repository import tokenRepository, userRepository
from app.modules.auth.Schemas.user import UserLogin, UserRegister
from app.modules.auth.Services.password_service import passwordService
from app.modules.auth.Services.token_service import tokenService


class AuthService:
    def __init__(self) -> None:
        self.user_repository = userRepository
        self.token_repository = tokenRepository
        self.password_service = passwordService
        self.token_service = tokenService
        self.auth_rules = authRules
        self.event_dispatcher = authEventDispatcher

    def _commit(self, db: Session) -> None:
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise

    def register(self, user: UserRegister, db: Session) -> User:
        existing_user = self.user_repository.get_by_email(db, user.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        try:
            role = self.auth_rules.parse_user_role(user.role)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid role") from exc

        new_user = self.user_repository.create(
            db,
            email=user.email,
            full_name=user.full_name,
            role=role,
            hashed_password=self.password_service.hash(user.password),
        )
        if new_user.id is None:
            raise HTTPException(status_code=500, detail="User creation failed")

        self._commit(db)
        self.event_dispatcher.dispatch(
            UserRegistered(
                user_id=new_user.id,
                email=new_user.email,
                role=new_user.role.value,
            )
        )
        return new_user

    def login(self, user: UserLogin, db: Session) -> dict[str, str]:
        db_user = self.user_repository.get_by_email(db, user.email)
        if not db_user or not self.password_service.verify(
            user.password, db_user.hashed_password
        ):
            raise HTTPException(status_code=400, detail="Invalid credentials")

        access_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
        refresh_expires = timedelta(minutes=settings.jwt_refresh_token_expire_minutes)
        db_user_id = db_user.id
        if db_user_id is None:
            raise HTTPException(status_code=500, detail="User record is invalid")
        db_user_email = db_user.email
        db_user_role = db_user.role.value

        access_token = self.token_service.create_access_token(
            user_email=db_user_email,
            user_id=db_user_id,
            role=db_user_role,
            expires_delta=access_expires,
        )
        refresh_token = self.token_service.create_refresh_token(
            user_email=db_user_email,
            user_id=db_user_id,
            expires_delta=refresh_expires,
        )

        self.token_service.store_refresh_token(
            db,
            token=refresh_token,
            user_id=db_user_id,
            expires_delta=refresh_expires,
        )
        self._commit(db)

        self.event_dispatcher.dispatch(
            UserLoggedIn(user_id=db_user_id, email=db_user_email)
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    def refresh(self, refresh_token: str, db: Session) -> dict[str, str | None]:
        payload = self.token_service.verify_refresh_token(refresh_token, db)
        user_id = payload["user_id"]
        email = payload["email"]

        db_user = self.user_repository.get_by_id(db, int(user_id))

        if not db_user:
            raise HTTPException(status_code=401, detail="User not found")
        db_user_id = db_user.id

        if db_user_id is None:
            raise HTTPException(status_code=500, detail="User record is invalid")

        db_user_email = db_user.email
        db_user_role = db_user.role.value

        access_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
        new_access_token = self.token_service.create_access_token(
            user_email=email,
            user_id=db_user_id,
            role=db_user_role,
            expires_delta=access_expires,
        )

        self.event_dispatcher.dispatch(
            TokenRefreshed(user_id=db_user_id, email=db_user_email)
        )
        return {
            "access_token": new_access_token,
            "refresh_token": None,
            "token_type": "bearer",
        }

    def logout(self, refresh_token: str, db: Session) -> dict[str, str]:
        db_token = self.token_repository.get_by_token(db, refresh_token)
        if not db_token:
            raise HTTPException(status_code=400, detail="Invalid refresh token")

        self.token_repository.revoke(db, db_token)
        self._commit(db)
        self.event_dispatcher.dispatch(
            UserLoggedOut(user_id=db_token.user_id, token_id=db_token.id)
        )
        return {"message": "Refresh token revoked successfully"}

    def get_me(self, current_user: User) -> User:
        return current_user

    def build_role_message(self, message: str, current_user: User) -> dict[str, str]:
        return {
            "message": message,
            "user": current_user.full_name,
            "role": current_user.role.value,
        }


authService = AuthService()
