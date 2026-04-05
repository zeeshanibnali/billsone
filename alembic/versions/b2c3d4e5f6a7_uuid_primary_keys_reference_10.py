"""uuid primary keys and varchar(10) reference

Revision ID: b2c3d4e5f6a7
Revises: f8a9b0c1d2e4
Create Date: 2026-04-06

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, Sequence[str], None] = "f8a9b0c1d2e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.text(
            "ALTER TABLE sub_bills DROP CONSTRAINT IF EXISTS sub_bills_bill_id_fkey"
        )
    )
    op.execute(sa.text("DROP INDEX IF EXISTS ix_sub_bills_reference_ci"))
    op.execute(sa.text("DROP INDEX IF EXISTS ix_bills_id"))
    op.execute(sa.text("DROP INDEX IF EXISTS ix_sub_bills_id"))

    op.execute(
        sa.text(
            "ALTER TABLE bills ADD COLUMN id_uuid UUID NOT NULL DEFAULT gen_random_uuid()"
        ),
    )
    op.execute(sa.text("ALTER TABLE sub_bills ADD COLUMN bill_uuid UUID"))
    op.execute(
        sa.text(
            "UPDATE sub_bills s SET bill_uuid = b.id_uuid FROM bills b "
            "WHERE s.bill_id = b.id",
        ),
    )
    op.execute(sa.text("ALTER TABLE sub_bills ALTER COLUMN bill_uuid SET NOT NULL"))
    op.execute(
        sa.text(
            "ALTER TABLE sub_bills ADD COLUMN id_uuid UUID NOT NULL DEFAULT gen_random_uuid()",
        ),
    )

    op.execute(sa.text("ALTER TABLE sub_bills DROP CONSTRAINT sub_bills_pkey"))
    op.execute(sa.text("ALTER TABLE sub_bills DROP COLUMN id"))
    op.execute(sa.text("ALTER TABLE sub_bills DROP COLUMN bill_id"))
    op.execute(sa.text("ALTER TABLE sub_bills RENAME COLUMN id_uuid TO id"))
    op.execute(sa.text("ALTER TABLE sub_bills RENAME COLUMN bill_uuid TO bill_id"))
    op.execute(sa.text("ALTER TABLE sub_bills ADD PRIMARY KEY (id)"))

    op.execute(sa.text("ALTER TABLE bills DROP CONSTRAINT bills_pkey"))
    op.execute(sa.text("ALTER TABLE bills DROP COLUMN id"))
    op.execute(sa.text("ALTER TABLE bills RENAME COLUMN id_uuid TO id"))
    op.execute(sa.text("ALTER TABLE bills ADD PRIMARY KEY (id)"))

    op.execute(
        sa.text(
            "ALTER TABLE sub_bills ADD CONSTRAINT sub_bills_bill_id_fkey "
            "FOREIGN KEY (bill_id) REFERENCES bills (id)",
        ),
    )
    op.execute(
        sa.text(
            "CREATE UNIQUE INDEX ix_sub_bills_reference_ci ON sub_bills (lower(reference))",
        ),
    )

    op.execute(
        sa.text(
            "ALTER TABLE sub_bills ALTER COLUMN reference TYPE VARCHAR(10) "
            "USING left(trim(reference::text), 10)",
        ),
    )


def downgrade() -> None:
    raise NotImplementedError(
        "Downgrade from UUID primary keys is not supported; restore from backup instead.",
    )
