from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field


class PaymentStatus(str, Enum):
    CREATED = "created"
    PAID = "paid"
    FAILED = "failed"


class PaymentSchema(BaseModel):
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

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "userId": "user_123",
                "orderId": "order_789",
                "paymentId": "pay_456",
                "amount": 499.00,
                "currency": "INR",
                "credits": 100,
                "plan": "pro",
                "status": "created"
            }
        }