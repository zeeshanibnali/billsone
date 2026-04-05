from decimal import Decimal
from typing import Any, Dict, Optional

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import contains_eager

from app.core.exceptions import ReferenceConflictError
from app.database.engine import SessionLocal
from app.modules.bills.bills_constants import MAX_SUB_BILLS_PER_BILL
from app.modules.bills.bills_entity import BillEntity
from app.modules.sub_bills.sub_bills_entity import SubBillEntity


def _is_unique_violation(exc: IntegrityError) -> bool:
    """True when PostgreSQL reports unique_violation (SQLSTATE 23505)."""
    orig = getattr(exc, "orig", None)
    if orig is None:
        return False
    code = getattr(orig, "pgcode", None) or getattr(orig, "sqlstate", None)
    return code == "23505"


_LIKE_ESCAPE = "\\"


def _escape_like_literal(text: str) -> str:
    """Escape \\, %, and _ so LIKE treats them as literals (with ESCAPE '\\')."""
    out: list[str] = []
    for ch in text:
        if ch == "\\":
            out.append("\\\\")
        elif ch == "%":
            out.append("\\%")
        elif ch == "_":
            out.append("\\_")
        else:
            out.append(ch)
    return "".join(out)


def _reference_like_pattern(reference: str) -> str:
    return f"%{_escape_like_literal(reference.lower())}%"


def _serialize_bill(bill: BillEntity) -> Dict[str, Any]:
    """
    Serialize a BillEntity into a dict.

    Assumes that bill.sub_bills already contains only the sub-bills that
    should be exposed (e.g. filtered in the query when needed).
    """
    return {
        "id": bill.id,
        "total": bill.total,
        "created_at": bill.created_at,
        "updated_at": bill.updated_at,
        "sub_bills": [
            {
                "id": sb.id,
                "amount": sb.amount,
                "reference": sb.reference,
                "created_at": sb.created_at,
                "updated_at": sb.updated_at,
            }
            for sb in (bill.sub_bills or [])
        ],
    }


def fetch_bills_paginated(
    *,
    reference: Optional[str] = None,
    total_from: Optional[Decimal] = None,
    total_to: Optional[Decimal] = None,
    skip: int = 0,
    limit: int = 50,
) -> Dict[str, Any]:
    """
    Fetch bills with optional filters, total count, and offset/limit pagination.

    Pagination applies to **bills** (each item in ``items`` is one bill). If ``reference``
    is set, each bill's ``sub_bills`` only includes rows whose reference matches the
    substring (case-insensitive); otherwise every sub-bill for that bill is included.
    """
    db = SessionLocal()
    try:
        if not reference:
            q = db.query(BillEntity)
            if total_from is not None:
                q = q.filter(BillEntity.total >= total_from)
            if total_to is not None:
                q = q.filter(BillEntity.total <= total_to)
            total = q.count()
            bills = (
                q.order_by(BillEntity.created_at.desc(), BillEntity.id)
                .offset(skip)
                .limit(limit)
                .all()
            )
            items = [_serialize_bill(b) for b in bills]
            return {"items": items, "total": total, "skip": skip, "limit": limit}

        pattern = _reference_like_pattern(reference)

        sub_bills_q = (
            db.query(SubBillEntity.bill_id)
            .filter(
                SubBillEntity.reference.isnot(None),
                func.lower(SubBillEntity.reference).like(
                    pattern,
                    escape=_LIKE_ESCAPE,
                ),
            )
            .distinct()
            .subquery()
        )

        filtered = (
            db.query(BillEntity)
            .join(sub_bills_q, BillEntity.id == sub_bills_q.c.bill_id)
            .join(BillEntity.sub_bills)
            .filter(
                func.lower(SubBillEntity.reference).like(
                    pattern,
                    escape=_LIKE_ESCAPE,
                ),
            )
        )
        if total_from is not None:
            filtered = filtered.filter(BillEntity.total >= total_from)
        if total_to is not None:
            filtered = filtered.filter(BillEntity.total <= total_to)

        matching_ids_sq = (
            filtered.with_entities(BillEntity.id.label("bid")).distinct().subquery()
        )
        total = db.query(func.count()).select_from(matching_ids_sq).scalar() or 0

        page_rows = (
            db.query(BillEntity.id)
            .select_from(BillEntity)
            .join(matching_ids_sq, BillEntity.id == matching_ids_sq.c.bid)
            .order_by(BillEntity.created_at.desc(), BillEntity.id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        bill_ids = [row[0] for row in page_rows]

        if not bill_ids:
            return {"items": [], "total": int(total), "skip": skip, "limit": limit}

        full = (
            db.query(BillEntity)
            .join(BillEntity.sub_bills)
            .filter(BillEntity.id.in_(bill_ids))
            .filter(
                func.lower(SubBillEntity.reference).like(
                    pattern,
                    escape=_LIKE_ESCAPE,
                ),
            )
            .options(contains_eager(BillEntity.sub_bills))
            .all()
        )
        by_id = {b.id: b for b in full}
        ordered_bills = [by_id[i] for i in bill_ids if i in by_id]
        items = [_serialize_bill(b) for b in ordered_bills]
        return {
            "items": items,
            "total": int(total),
            "skip": skip,
            "limit": limit,
        }
    finally:
        db.close()


def create_bill_with_sub_bills(payload: dict) -> Dict[str, Any]:
    """
    Create a bill and its sub-bills inside an explicit transaction so that
    either everything is persisted or nothing is.
    """
    sub_rows = payload.get("sub_bills") or []
    if len(sub_rows) > MAX_SUB_BILLS_PER_BILL:
        raise HTTPException(
            status_code=422,
            detail=(
                f"sub_bills cannot contain more than {MAX_SUB_BILLS_PER_BILL} items"
            ),
        )

    db = SessionLocal()
    try:
        bill = BillEntity(total=payload["total"])

        for sub_payload in sub_rows:
            sub_bill = SubBillEntity(
                amount=sub_payload["amount"],
                reference=sub_payload.get("reference"),
            )
            bill.sub_bills.append(sub_bill)

        db.add(bill)
        db.commit()
        db.refresh(bill)

        return {
            "id": bill.id,
            "total": bill.total,
            "created_at": bill.created_at,
            "updated_at": bill.updated_at,
            "sub_bills": [
                {
                    "id": sb.id,
                    "amount": sb.amount,
                    "reference": sb.reference,
                    "created_at": sb.created_at,
                    "updated_at": sb.updated_at,
                }
                for sb in bill.sub_bills
            ],
        }
    except IntegrityError as e:
        db.rollback()
        if _is_unique_violation(e):
            raise ReferenceConflictError(
                "A sub-bill with this reference already exists (uniqueness is case-insensitive).",
            ) from e
        raise
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
