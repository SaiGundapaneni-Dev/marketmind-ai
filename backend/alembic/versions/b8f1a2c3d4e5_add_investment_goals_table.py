"""add investment goals table

Revision ID: b8f1a2c3d4e5
Revises: 73f557678b28
Create Date: 2026-08-04 17:45:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "b8f1a2c3d4e5"
down_revision: Union[str, Sequence[str], None] = "73f557678b28"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "investment_goals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("category", sa.String(length=50), server_default="custom", nullable=False),
        sa.Column("target_amount", sa.Float(), nullable=False),
        sa.Column("current_amount", sa.Float(), server_default="0", nullable=False),
        sa.Column("monthly_contribution", sa.Float(), server_default="0", nullable=False),
        sa.Column("target_date", sa.Date(), nullable=False),
        sa.Column("priority", sa.String(length=20), server_default="medium", nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_investment_goals_id", "investment_goals", ["id"])
    op.create_index("ix_investment_goals_user_id", "investment_goals", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_investment_goals_user_id", table_name="investment_goals")
    op.drop_index("ix_investment_goals_id", table_name="investment_goals")
    op.drop_table("investment_goals")
