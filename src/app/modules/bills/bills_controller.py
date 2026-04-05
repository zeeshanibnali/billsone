from decimal import Decimal
from typing import Annotated, Optional

from fastapi import APIRouter, Query
from pydantic import Field

from app.core.logger import get_logger
from app.modules.bills.bills_constants import (
    DEFAULT_BILLS_PAGE_SIZE,
    MAX_BILLS_PAGE_SIZE,
)
from app.modules.bills.bills_schemas import BillCreate, BillOut, PaginatedBillsOut
from app.modules.bills.bills_service import (
    create_bill_with_sub_bills,
    fetch_bills_paginated,
)


logger = get_logger(__name__)
router = APIRouter(prefix="", tags=["Bills"])


def _normalize_reference_filter(reference: Optional[str]) -> Optional[str]:
    """Treat missing, empty, or whitespace-only reference as no filter."""
    if reference is None:
        return None
    stripped = reference.strip()
    return stripped if stripped else None


@router.get(
    "/bills",
    response_model=PaginatedBillsOut,
    summary="List bills (paginated)",
    description=(
        "Paginate **bills** (skip/limit apply to bill rows). "
        "Optional filter by sub-bill reference substring (case-insensitive): only bills with at least "
        "one matching sub-bill are listed, and each bill includes **only** matching sub-bills. "
        "Optional total_from / total_to filter bill total (inclusive); parsed as Decimal to match storage. "
        "Ordered by bill created_at (newest first), then id."
    ),
)
def read_bills(
    reference: Optional[str] = Query(
        default=None,
        description=(
            "Case-insensitive substring used to filter sub-bill references. "
            "Only matching sub-bills are returned per bill."
        ),
    ),
    total_from: Annotated[
        Optional[Decimal],
        Field(
            default=None,
            ge=Decimal("0"),
            max_digits=18,
            decimal_places=4,
            description=(
                "Minimum bill total (inclusive). Parsed as a decimal; same precision as bill totals."
            ),
        ),
        Query(),
    ] = None,
    total_to: Annotated[
        Optional[Decimal],
        Field(
            default=None,
            ge=Decimal("0"),
            max_digits=18,
            decimal_places=4,
            description=(
                "Maximum bill total (inclusive). Parsed as a decimal; same precision as bill totals."
            ),
        ),
        Query(),
    ] = None,
    skip: int = Query(
        0,
        ge=0,
        description="Number of bills to skip (offset into the filtered bill list).",
    ),
    limit: int = Query(
        DEFAULT_BILLS_PAGE_SIZE,
        ge=1,
        le=MAX_BILLS_PAGE_SIZE,
        description=(
            f"Maximum number of bills to return in this page (1–{MAX_BILLS_PAGE_SIZE}). "
            "Does not cap sub-bills per bill."
        ),
    ),
):
    """
    Returns a page of bills, optionally filtered by:

    - sub-bill reference substring (case-insensitive)
    - minimum/maximum bill total (inclusive)
    """
    logger.info(
        "Fetching bills",
        extra={
            "reference": reference,
            "total_from": total_from,
            "total_to": total_to,
            "skip": skip,
            "limit": limit,
        },
    )
    return fetch_bills_paginated(
        reference=_normalize_reference_filter(reference),
        total_from=total_from,
        total_to=total_to,
        skip=skip,
        limit=limit,
    )


@router.post(
    "/bills",
    response_model=BillOut,
    summary="Create a bill with sub-bills",
    description="Create a new bill along with its associated sub-bills in a single request.",
    responses={
        409: {
            "description": "Sub-bill reference already exists (uniqueness is case-insensitive).",
        },
        422: {
            "description": (
                "Request body failed validation (e.g. total vs sub-bills sum, duplicate "
                "non-null references in payload, reference length, or more than 500 sub-bills)."
            ),
        },
    },
)
def create_bill(payload: BillCreate):
    """
    Creates a new bill and its related sub-bills.
    """
    logger.info("Creating bill with sub-bills")
    return create_bill_with_sub_bills(payload.model_dump())
