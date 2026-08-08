"""Auth session cleanup

Revision ID: a3f1e8d9c4b2
Revises: c82632d6b4af
Create Date: 2026-08-08 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a3f1e8d9c4b2"
down_revision: Union[str, Sequence[str], None] = "c82632d6b4af"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column(
            "is_active",
            existing_type=sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        )
        batch_op.alter_column(
            "created_at",
            existing_type=sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        )
        batch_op.alter_column(
            "updated_at",
            existing_type=sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        )

    with op.batch_alter_table("tokens") as batch_op:
        batch_op.drop_column("is_refresh")
        batch_op.alter_column(
            "is_revoked",
            existing_type=sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("tokens") as batch_op:
        batch_op.add_column(
            sa.Column("is_refresh", sa.Boolean(), nullable=True, server_default=sa.false())
        )
        batch_op.alter_column(
            "is_revoked",
            existing_type=sa.Boolean(),
            nullable=False,
            server_default=None,
        )

    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column(
            "updated_at",
            existing_type=sa.DateTime(timezone=True),
            nullable=True,
            server_default=None,
        )
        batch_op.alter_column(
            "created_at",
            existing_type=sa.DateTime(timezone=True),
            nullable=True,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        )
        batch_op.alter_column(
            "is_active",
            existing_type=sa.Boolean(),
            nullable=True,
            server_default=None,
        )
