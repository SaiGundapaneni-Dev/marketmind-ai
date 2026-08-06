"""add investment thesis table

Revision ID: 73f557678b28
Revises: 1d5229668a3e
Create Date: 2026-07-20 16:58:27.337317
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "73f557678b28"
down_revision: Union[str, Sequence[str], None] = "1d5229668a3e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "investment_theses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("holding_id", sa.Integer(), nullable=False),
        sa.Column("thesis", sa.Text(), nullable=False),
        sa.Column("target_price", sa.Float(), nullable=True),
        sa.Column("investment_horizon", sa.String(length=50), nullable=True),
        sa.Column("conviction_score", sa.Integer(), nullable=True),
        sa.Column("risk_level", sa.String(length=30), nullable=True),
        sa.Column("buy_reasons", sa.Text(), nullable=True),
        sa.Column("sell_conditions", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("review_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["holding_id"], ["holdings.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("holding_id"),
    )
    op.create_index(
        op.f("ix_investment_theses_id"),
        "investment_theses",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_investment_theses_holding_id"),
        "investment_theses",
        ["holding_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_investment_theses_holding_id"),
        table_name="investment_theses",
    )
    op.drop_index(
        op.f("ix_investment_theses_id"),
        table_name="investment_theses",
    )
    op.drop_table("investment_theses")
