from decimal import Decimal
from typing import List

from sqlalchemy.orm import Session

from app.modules.bills.bills_entity import BillEntity
from app.modules.sub_bills.sub_bills_entity import SubBillEntity


def seed_db(db: Session) -> None:
    """
    Insert deterministic dummy data for local testing.

    This function is idempotent: if any bills already exist, it does nothing.
    """
    has_data = db.query(BillEntity).first()
    if has_data:
        return

    bills: List[BillEntity] = []

    # Bill 1: references fit VARCHAR(10)
    bill1 = BillEntity(total=Decimal("3.0000"))
    bill1.sub_bills.extend(
        [
            SubBillEntity(amount=Decimal("1.0000"), reference="ref1"),
            SubBillEntity(amount=Decimal("2.0000"), reference="ref2"),
        ],
    )
    bills.append(bill1)

    bill2 = BillEntity(total=Decimal("7.5000"))
    bill2.sub_bills.extend(
        [
            SubBillEntity(amount=Decimal("3.5000"), reference="REF-ABC"),
            SubBillEntity(amount=Decimal("4.0000"), reference="INV-001"),
        ],
    )
    bills.append(bill2)

    bill3 = BillEntity(total=Decimal("10.0000"))
    bill3.sub_bills.extend(
        [
            SubBillEntity(amount=Decimal("5.0000"), reference="subscript"),
            SubBillEntity(amount=Decimal("5.0000"), reference="INTERNAL"),
        ],
    )
    bills.append(bill3)

    db.add_all(bills)
    db.commit()
