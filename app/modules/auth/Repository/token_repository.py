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
        is_refresh: bool = False,
    ) -> Token:
        db_token = Token(
            token=token,
            user_id=user_id,
            expired_at=expired_at,
            is_revoked=False,
            is_refresh=is_refresh,
        )
        db.add(db_token)
        db.commit()
        db.refresh(db_token)
        return db_token

    def get_by_token(
        self, db: Session, token: str, is_refresh: bool | None = None
    ) -> Token | None:
        query = db.query(Token).filter(Token.token == token)
        if is_refresh is not None:
            query = query.filter(Token.is_refresh == is_refresh)
        return query.first()

    def revoke(self, db: Session, db_token: Token) -> Token:
        db_token.is_revoked = True
        db.commit()
        db.refresh(db_token)
        return db_token


tokenRepository = TokenRepository()
