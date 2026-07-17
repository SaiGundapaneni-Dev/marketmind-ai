"""scope portfolio snapshots to portfolio

Revision ID: 1d5229668a3e
Revises: 1ea606e5bdbf
Create Date: 2026-07-15 11:10:08.321329

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1d5229668a3e'
down_revision: Union[str, Sequence[str], None] = '1ea606e5bdbf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "portfolio_snapshots",
        sa.Column(
            "portfolio_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.create_index(
        op.f("ix_portfolio_snapshots_portfolio_id"),
        "portfolio_snapshots",
        ["portfolio_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_portfolio_snapshots_portfolio_id",
        "portfolio_snapshots",
        "portfolios",
        ["portfolio_id"],
        ["id"],
    )

    op.execute(
        """
        UPDATE portfolio_snapshots
        SET portfolio_id = (
            SELECT id
            FROM portfolios
            ORDER BY id
            LIMIT 1
        )
        WHERE portfolio_id IS NULL
        """
    )

    op.alter_column(
        "portfolio_snapshots",
        "portfolio_id",
        existing_type=sa.Integer(),
        nullable=False,
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_portfolio_snapshots_portfolio_id",
        "portfolio_snapshots",
        type_="foreignkey",
    )

    op.drop_index(
        op.f("ix_portfolio_snapshots_portfolio_id"),
        table_name="portfolio_snapshots",
    )

    op.drop_column(
        "portfolio_snapshots",
        "portfolio_id",
    )