"""sub_bills reference globally unique

Revision ID: d5e6f7a8b9c0
Revises: c4f8a1b2d3e4
Create Date: 2026-04-06

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d5e6f7a8b9c0"
down_revision: Union[str, Sequence[str], None] = "c4f8a1b2d3e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index("ix_sub_bills_bill_id_reference_ci", table_name="sub_bills")
    op.create_index(
        "ix_sub_bills_reference_ci",
        "sub_bills",
        [sa.literal_column("lower(reference)")],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_sub_bills_reference_ci", table_name="sub_bills")
    op.create_index(
        "ix_sub_bills_bill_id_reference_ci",
        "sub_bills",
        ["bill_id", sa.literal_column("lower(reference)")],
        unique=True,
    )
