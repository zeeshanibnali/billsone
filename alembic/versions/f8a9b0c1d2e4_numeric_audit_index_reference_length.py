"""numeric money, audit timestamps, bills total index, reference varchar

Revision ID: f8a9b0c1d2e4
Revises: e6f7a8b9c0d1
Create Date: 2026-04-06

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f8a9b0c1d2e4"
down_revision: Union[str, Sequence[str], None] = "e6f7a8b9c0d1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "bills",
        "total",
        existing_type=sa.Float(),
        type_=sa.Numeric(18, 4),
        existing_nullable=False,
        postgresql_using="total::numeric(18,4)",
    )
    op.alter_column(
        "sub_bills",
        "amount",
        existing_type=sa.Float(),
        type_=sa.Numeric(18, 4),
        existing_nullable=False,
        postgresql_using="amount::numeric(18,4)",
    )
    op.alter_column(
        "sub_bills",
        "reference",
        existing_type=sa.String(),
        type_=sa.String(128),
        existing_nullable=False,
        postgresql_using="reference::varchar(128)",
    )

    op.add_column(
        "bills",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )
    op.add_column(
        "bills",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )
    op.add_column(
        "sub_bills",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )
    op.add_column(
        "sub_bills",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )

    op.create_index("ix_bills_total", "bills", ["total"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_bills_total", table_name="bills")

    op.drop_column("sub_bills", "updated_at")
    op.drop_column("sub_bills", "created_at")
    op.drop_column("bills", "updated_at")
    op.drop_column("bills", "created_at")

    op.alter_column(
        "sub_bills",
        "reference",
        existing_type=sa.String(128),
        type_=sa.String(),
        existing_nullable=False,
    )
    op.alter_column(
        "sub_bills",
        "amount",
        existing_type=sa.Numeric(18, 4),
        type_=sa.Float(),
        existing_nullable=False,
        postgresql_using="amount::double precision",
    )
    op.alter_column(
        "bills",
        "total",
        existing_type=sa.Numeric(18, 4),
        type_=sa.Float(),
        existing_nullable=False,
        postgresql_using="total::double precision",
    )
