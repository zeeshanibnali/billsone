# app/bills/bill_controller.py

from fastapi import APIRouter
from app.modules.bills.bills_service import fetch_all_bills

router = APIRouter()


@router.get("/bills")
def read_bills():
    return fetch_all_bills()
