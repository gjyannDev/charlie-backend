"""
Token and current-user services for the auth module.
"""

from datetime import UTC, datetime, timedelta
from typing import TypedDict

from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import Token, User
from app.modules.auth.Repository import tokenRepository, userRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.login_url)


class TokenPayload(TypedDict):
    email: str
    exp: int
    user_id: int
    role: str | None
    permissions: list[str]


class TokenService:
    def __init__(self) -> None:
        self.token_repository = tokenRepository
        self.user_repository = userRepository

    def create_access_token(
        self,
        user_email: str,
        user_id: int,
        expires_delta: timedelta | None = None,
        role: str | None = None,
        permissions: list[str] | None = None,
    ) -> str:
        expires_delta = expires_delta or timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )
        expire_time = datetime.now(UTC) + expires_delta
        payload = {
            "email": user_email,
            "exp": expire_time,
            "user_id": user_id,
            "role": role,
            "permissions": permissions or [],
        }
        return jwt.encode(
            payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
        )

    def create_refresh_token(
        self, user_email: str, user_id: int, expires_delta: timedelta | None = None
    ) -> str:
        expires_delta = expires_delta or timedelta(
            minutes=settings.jwt_refresh_token_expire_minutes
        )
        expire_time = datetime.now(UTC) + expires_delta
        payload = {
            "email": user_email,
            "exp": expire_time,
            "user_id": user_id,
        }
        return jwt.encode(
            payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
        )

    def decode_token(self, token: str) -> TokenPayload:
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
            )
            return {
                "email": str(payload["email"]),
                "exp": int(payload["exp"]),
                "user_id": int(payload["user_id"]),
                "role": payload.get("role"),
                "permissions": list(payload.get("permissions", [])),
            }
        except ExpiredSignatureError as exc:
            raise HTTPException(status_code=498, detail="Token expired") from exc
        except JWTError as exc:
            raise HTTPException(status_code=401, detail="Invalid token") from exc

    def store_refresh_token(
        self,
        db: Session,
        token: str,
        user_id: int,
        expires_delta: timedelta,
    ) -> Token:
        expire_time = datetime.now(UTC) + expires_delta
        return self.token_repository.create(
            db,
            token=token,
            user_id=user_id,
            expired_at=expire_time,
        )

    def verify_refresh_token(self, token: str, db: Session) -> TokenPayload:
        payload = self.decode_token(token)
        db_token = self.token_repository.get_by_token(db, token)
        if not db_token:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        if db_token.is_revoked:
            raise HTTPException(status_code=401, detail="Refresh token revoked")
        if self._is_expired(db_token.expired_at):
            raise HTTPException(status_code=498, detail="Refresh token expired")
        return payload

    def _is_expired(self, expired_at: datetime) -> bool:
        now = datetime.now(UTC)
        if expired_at.tzinfo is None:
            return expired_at <= now.replace(tzinfo=None)
        return expired_at <= now

    def get_current_user(self, token: str, db: Session) -> User:
        payload = self.decode_token(token)
        user = self.user_repository.get_by_id(db, int(payload["user_id"]))
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user

    def verify_token(self, token: str, db: Session, is_refresh: bool = False) -> TokenPayload:
        if is_refresh:
            return self.verify_refresh_token(token, db)
        return self.decode_token(token)

    def store_token(
        self,
        db: Session,
        token: str,
        user_id: int,
        expires_delta: timedelta,
        is_refresh: bool = False,
    ) -> Token:
        if not is_refresh:
            raise ValueError("Access tokens are not persisted")
        return self.store_refresh_token(db, token, user_id, expires_delta)


tokenService = TokenService()


def get_current_user(
    token: str = Security(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    return tokenService.get_current_user(token, db)
