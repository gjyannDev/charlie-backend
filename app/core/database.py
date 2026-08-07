"""
database.py - Database configuration and session management.

This module sets up the SQLAlchemy engine and session maker.
It reuses the shared declarative Base from app.models.base so the
application, models, and Alembic all operate on the same metadata.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.base import Base

# -------------------------------------------------------------------
# Engine configuration
# -------------------------------------------------------------------
# `check_same_thread=False` is required only for SQLite to allow usage in async environments.
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)

# -------------------------------------------------------------------
# SessionLocal factory
# -------------------------------------------------------------------
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# -------------------------------------------------------------------
# Dependency
# -------------------------------------------------------------------
def get_db():
    """
    Dependency that provides a SQLAlchemy database session.

    Yields:
        db (Session): A database session that is automatically closed after use.

    Usage:
        - Import `get_db` and use it in FastAPI endpoints with `Depends`.
        - Example:
            def get_users(db: Session = Depends(get_db)):
                return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
