from datetime import datetime
from decimal import Decimal
from typing import Annotated, Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

from app.modules.bills.bills_constants import (
    MAX_SUB_BILLS_PER_BILL,
    REFERENCE_MAX_LENGTH,
)

Money = Annotated[
    Decimal,
    Field(
        max_digits=18,
        decimal_places=4,
        ge=0,
        description="Monetary amount (4 decimal places)",
    ),
]


class SubBillIn(BaseModel):
    amount: Money = Field(..., description="Amount of the sub-bill")
    reference: Optional[str] = Field(
        default=None,
        max_length=REFERENCE_MAX_LENGTH,
        description=(
            "Optional line-item reference; when set, must be unique across all sub-bills "
            "(case-insensitive). Omit or null for line items without a reference."
        ),
        examples=["REF1"],
    )

    @field_validator("reference", mode="before")
    @classmethod
    def normalize_reference(cls, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, str):
            stripped = value.strip()
            return stripped if stripped else None
        return value


class BillCreate(BaseModel):
    total: Money = Field(..., description="Total amount of the bill")
    sub_bills: List[SubBillIn] = Field(
        ...,
        description=(
            "List of sub-bills associated with this bill (may be empty if total is 0). "
            f"At most {MAX_SUB_BILLS_PER_BILL} items."
        ),
    )

    @model_validator(mode="before")
    @classmethod
    def reject_too_many_sub_bills(cls, data: Any) -> Any:
        if isinstance(data, dict):
            raw = data.get("sub_bills")
            if isinstance(raw, list) and len(raw) > MAX_SUB_BILLS_PER_BILL:
                raise ValueError(
                    f"sub_bills cannot contain more than {MAX_SUB_BILLS_PER_BILL} items",
                )
        return data

    @model_validator(mode="after")
    def validate_total_matches_sub_bills(self) -> "BillCreate":
        sub_total = sum((sb.amount for sb in self.sub_bills), Decimal("0"))
        if self.total != sub_total:
            raise ValueError(
                "total must equal the sum of sub_bills.amount values",
            )
        return self

    @model_validator(mode="after")
    def validate_unique_references_in_payload(self) -> "BillCreate":
        lowered = [
            sb.reference.lower() for sb in self.sub_bills if sb.reference is not None
        ]
        if len(lowered) != len(set(lowered)):
            raise ValueError(
                "sub_bills must not contain duplicate non-null references (case-insensitive)",
            )
        return self


class SubBillOut(BaseModel):
    id: UUID
    amount: Money
    reference: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class BillOut(BaseModel):
    id: UUID
    total: Money
    created_at: datetime
    updated_at: datetime
    sub_bills: List[SubBillOut]


class PaginatedBillsOut(BaseModel):
    items: List[BillOut]
    total: int = Field(..., description="Total rows matching filters (all pages)")
    skip: int = Field(..., description="Number of rows skipped from the start")
    limit: int = Field(..., description="Maximum rows returned in this page")
