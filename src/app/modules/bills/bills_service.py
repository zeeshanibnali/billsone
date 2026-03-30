# app/bills/bill_service.py

from app.database.engine import get_all_bills


def fetch_all_bills():
    bills = get_all_bills()

    return [{"id": b.id, "name": b.name, "amount": b.amount} for b in bills]
