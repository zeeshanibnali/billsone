import uuid

from sqlalchemy import Column, DateTime, Numeric, Uuid, text
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.database.utc_datetime import utc_now


class BillEntity(Base):
    """
    Bill aggregate root. Timestamps are UTC ``timestamptz``; see ``utc_now`` and engine ``timezone=UTC``.
    """

    __tablename__ = "bills"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    total = Column(Numeric(18, 4), nullable=False)
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
    sub_bills = relationship(
        "SubBillEntity",
        back_populates="bill",
        cascade="all, delete-orphan",
    )
