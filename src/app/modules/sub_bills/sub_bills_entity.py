import uuid

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Uuid,
    func,
    text,
)
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.database.utc_datetime import utc_now
from app.modules.bills.bills_constants import REFERENCE_MAX_LENGTH


class SubBillEntity(Base):
    """
    Line items under a bill.

    ``created_at`` / ``updated_at`` are PostgreSQL ``timestamptz``, persisted in UTC via
    ``utc_now`` (ORM) and ``CURRENT_TIMESTAMP`` (server default) under a UTC DB session
    (see ``app.database.engine``). Matches ``BillEntity`` timestamp behavior.
    """

    __tablename__ = "sub_bills"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    amount = Column(Numeric(18, 4), nullable=False)
    reference = Column(String(REFERENCE_MAX_LENGTH), nullable=True)
    bill_id = Column(Uuid(as_uuid=True), ForeignKey("bills.id"), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    bill = relationship("BillEntity", back_populates="sub_bills")

    # Non-null references are unique case-insensitively; multiple NULLs are allowed.
    __table_args__ = (
        Index(
            "ix_sub_bills_reference_ci",
            func.lower(reference),
            unique=True,
            postgresql_where=(reference.isnot(None)),
        ),
    )
