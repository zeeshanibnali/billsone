"""drop foo from bills

Revision ID: c4f8a1b2d3e4
Revises: 0aa90d240f13
Create Date: 2026-04-05

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c4f8a1b2d3e4"
down_revision: Union[str, Sequence[str], None] = "0aa90d240f13"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("bills", "foo")


def downgrade() -> None:
    op.add_column(
        "bills",
        sa.Column("foo", sa.String(), nullable=True),
    )
