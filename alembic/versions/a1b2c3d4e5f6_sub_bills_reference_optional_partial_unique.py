"""sub_bills.reference nullable; partial unique index on lower(reference)

Revision ID: a1b2c3d4e5f6
Revises: b2c3d4e5f6a7
Create Date: 2026-04-06

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(sa.text("DROP INDEX IF EXISTS ix_sub_bills_reference_ci"))
    op.execute(
        sa.text("ALTER TABLE sub_bills ALTER COLUMN reference DROP NOT NULL"),
    )
    op.execute(
        sa.text(
            "CREATE UNIQUE INDEX ix_sub_bills_reference_ci ON sub_bills "
            "(lower(reference)) WHERE reference IS NOT NULL",
        ),
    )


def downgrade() -> None:
    op.execute(sa.text("DROP INDEX IF EXISTS ix_sub_bills_reference_ci"))
    op.execute(
        sa.text(
            "DELETE FROM sub_bills WHERE reference IS NULL",
        ),
    )
    op.execute(
        sa.text("ALTER TABLE sub_bills ALTER COLUMN reference SET NOT NULL"),
    )
    op.execute(
        sa.text(
            "CREATE UNIQUE INDEX ix_sub_bills_reference_ci ON sub_bills (lower(reference))",
        ),
    )
