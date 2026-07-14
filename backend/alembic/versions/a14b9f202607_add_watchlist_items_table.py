"""add watchlist items table

Revision ID: a14b9f202607
Revises: 83d59ea767b6
Create Date: 2026-07-14 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a14b9f202607"
down_revision: Union[str, Sequence[str], None] = "83d59ea767b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "watchlist_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("symbol", sa.String(), nullable=False),
        sa.Column("company_name", sa.String(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "symbol",
            name="uq_watchlist_user_symbol",
        ),
    )
    op.create_index(
        op.f("ix_watchlist_items_id"),
        "watchlist_items",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_watchlist_items_symbol"),
        "watchlist_items",
        ["symbol"],
        unique=False,
    )
    op.create_index(
        op.f("ix_watchlist_items_user_id"),
        "watchlist_items",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_watchlist_items_user_id"),
        table_name="watchlist_items",
    )
    op.drop_index(
        op.f("ix_watchlist_items_symbol"),
        table_name="watchlist_items",
    )
    op.drop_index(
        op.f("ix_watchlist_items_id"),
        table_name="watchlist_items",
    )
    op.drop_table("watchlist_items")
