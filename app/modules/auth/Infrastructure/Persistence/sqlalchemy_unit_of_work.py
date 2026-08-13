"""
SQLAlchemy unit-of-work implementation.
"""

from typing import Any


class SQLAlchemyUnitOfWork:
    def commit(self, db: Any) -> None:
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise


sqlalchemyUnitOfWork = SQLAlchemyUnitOfWork()
