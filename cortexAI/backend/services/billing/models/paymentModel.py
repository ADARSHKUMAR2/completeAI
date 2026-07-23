# models/paymentModel.py
from datetime import datetime
from typing import Optional
from enum import Enum
from beanie import Document
from pydantic import Field


class PaymentStatus(str, Enum):
    CREATED = "created"
    PAID = "paid"
    FAILED = "failed"


class Payment(Document):
    user_id: str = Field(..., alias="userId")
    order_id: str = Field(..., alias="orderId")
    payment_id: Optional[str] = Field(None, alias="paymentId")
    amount: Optional[float] = None
    currency: str = "INR"
    credits: Optional[int] = None
    plan: Optional[str] = None
    status: PaymentStatus = PaymentStatus.CREATED
    created_at: datetime = Field(default_factory=datetime.utcnow, alias="createdAt")
    updated_at: datetime = Field(default_factory=datetime.utcnow, alias="updatedAt")

    class Settings:
        name = "payments"  # Collection name in MongoDB

    class Config:
        populate_by_name = True