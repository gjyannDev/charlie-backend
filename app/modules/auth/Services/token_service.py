"""
Token and current-user services for the auth module.
"""

from datetime import UTC, datetime, timedelta

from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import Token, User
from app.modules.auth.Repository import tokenRepository, userRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.login_url)


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

    def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
            )
        except ExpiredSignatureError as exc:
            raise HTTPException(status_code=498, detail="Token expired") from exc
        except JWTError as exc:
            raise HTTPException(status_code=401, detail="Invalid token") from exc

    def store_token(
        self,
        db: Session,
        token: str,
        user_id: int,
        expires_delta: timedelta,
        is_refresh: bool = False,
    ) -> Token:
        expire_time = datetime.now(UTC) + expires_delta
        return self.token_repository.create(
            db,
            token=token,
            user_id=user_id,
            expired_at=expire_time,
            is_refresh=is_refresh,
        )

    def verify_token(self, token: str, db: Session, is_refresh: bool = False) -> dict:
        payload = self.decode_token(token)
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        db_token = self.token_repository.get_by_token(db, token, is_refresh=is_refresh)
        if not db_token or db_token.is_revoked:
            raise HTTPException(status_code=401, detail="Token revoked or invalid")

        return payload

    def get_current_user(self, token: str, db: Session) -> User:
        payload = self.verify_token(token, db, is_refresh=False)
        user_id = payload.get("user_id")
        user = self.user_repository.get_by_id(db, int(user_id))
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user


tokenService = TokenService()


def get_current_user(
    token: str = Security(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    return tokenService.get_current_user(token, db)
