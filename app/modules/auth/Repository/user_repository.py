"""
User persistence operations for the auth module.
"""

from sqlalchemy.orm import Session

from app.models.user import User
from app.modules.auth.Domain.Enums import UserRole


class UserRepository:
    def get_by_email(self, db: Session, email: str) -> User | None:
        return db.query(User).filter(User.email == email).first()

    def get_by_id(self, db: Session, user_id: int) -> User | None:
        return db.query(User).filter(User.id == user_id).first()

    def create(
        self,
        db: Session,
        *,
        email: str,
        full_name: str,
        role: UserRole,
        hashed_password: str,
    ) -> User:
        user = User(
            email=email,
            full_name=full_name,
            role=role,
            hashed_password=hashed_password,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


userRepository = UserRepository()
