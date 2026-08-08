"""
users.py - SQLAlchemy models for User and Token.

Defines the User and Token models used by the auth module.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.auth.Domain.Enums import UserRole

from .base import Base


class User(Base):
    """
    Represents an application user.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=func.true(),
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    tokens: Mapped[list["Token"]] = relationship(
        "Token",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Token(Base):
    """
    Represents a refresh token issued to a user.
    """

    __tablename__ = "tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    token: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    expired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_revoked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=func.false(),
    )

    user: Mapped[User] = relationship("User", back_populates="tokens")
