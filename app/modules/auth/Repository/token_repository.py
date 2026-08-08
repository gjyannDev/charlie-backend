"""
Token persistence operations for the auth module.
"""

from datetime import datetime

from sqlalchemy.orm import Session

from app.models.user import Token


class TokenRepository:
    def create(
        self,
        db: Session,
        *,
        token: str,
        user_id: int,
        expired_at: datetime,
    ) -> Token:
        db_token = Token(
            token=token,
            user_id=user_id,
            expired_at=expired_at,
            is_revoked=False,
        )
        db.add(db_token)
        db.flush()
        db.refresh(db_token)
        return db_token

    def get_by_token(self, db: Session, token: str) -> Token | None:
        return db.query(Token).filter(Token.token == token).first()

    def revoke(self, db: Session, db_token: Token) -> Token:
        db_token.is_revoked = True
        db.flush()
        db.refresh(db_token)
        return db_token


tokenRepository = TokenRepository()
