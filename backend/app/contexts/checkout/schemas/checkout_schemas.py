from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class CompleteCheckoutRequest(BaseModel):
    pending_order_id: int
    payment_method: Literal["cash", "card", "upi"]


class BillResponse(BaseModel):
    subtotal: float
    gst_rate: float
    gst_amount: float
    total_amount: float


class CompleteCheckoutResponse(BaseModel):
    order_id: int
    status: str
    bill: BillResponse
    payment_method: str
    paid_at: datetime
