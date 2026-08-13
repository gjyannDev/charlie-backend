"""
HTTP dependencies for auth.
"""

from fastapi import Depends, Security
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.modules.auth.Infrastructure.Security import jwtTokenIssuer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.login_url)


def get_current_user(
    token: str = Security(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    return jwtTokenIssuer.get_current_user(token, db)
