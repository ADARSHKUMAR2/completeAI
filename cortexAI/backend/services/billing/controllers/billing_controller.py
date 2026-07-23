import time
import os
import hmac
import hashlib
import httpx
from fastapi import HTTPException, status
from pydantic import BaseModel

from config.Plans import PLANS
from config.razorpay import razorpay_client
from models.paymentModel import Payment, PaymentStatus


class CreateOrderSchema(BaseModel):
    plan: str


class VerifyPaymentSchema(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://127.0.0.1:8001")


async def create_order(body: CreateOrderSchema, user_id: str):
    """
    Creates a new Razorpay payment order and stores initial record in MongoDB.
    """
    if not user_id or not isinstance(user_id, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing or invalid user id"
        )

    if not getattr(razorpay_client, "order", None):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Razorpay client is not configured"
        )

    try:
        plan_key = body.plan.lower()
        selected_plan = PLANS.get(plan_key)

        if not selected_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="plan not found"
            )

        if isinstance(selected_plan, dict):
            plan_amount = selected_plan["amount"]
            plan_credits = selected_plan["credits"]
            plan_id = selected_plan.get("id", plan_key)
            plan_name = selected_plan.get("name", plan_key)
        else:  # If object/Pydantic model
            plan_amount = getattr(selected_plan, "amount")
            plan_credits = getattr(selected_plan, "credits")
            plan_id = getattr(selected_plan, "id", plan_key)
            plan_name = getattr(selected_plan, "name", plan_key)

        order_amount_in_paise = int(plan_amount * 100)

        # Create Razorpay order
        order_payload = {
            "amount": order_amount_in_paise,  # Amount in paise
            "currency": "INR",
            "receipt": f"receipt-{int(time.time() * 1000)}"
        }
        order = razorpay_client.order.create(data=order_payload)

        # Create and save Beanie document using standard Python attribute names
        new_payment = Payment(
            user_id=user_id,
            order_id=order["id"],
            amount=plan_amount,
            credits=plan_credits,
            plan=plan_id,
            currency=order["currency"],
            status=PaymentStatus.CREATED
        )

        await new_payment.insert()

        return {
            "order": order,
            "plan": {
                "id": plan_id,
                "name": plan_name,
                "amount": plan_amount,
                "credits": plan_credits
            }
        }

    except HTTPException:
        raise
    except Exception as error:
        print(f"❌ Error creating order: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"create order error {str(error)}"
        )


async def verify_payment(body: VerifyPaymentSchema):
    """
    Verifies Razorpay payment HMAC signature and marks payment as PAID in MongoDB.
    """
    try:
        # 1. Generate HMAC-SHA256 signature
        secret = os.getenv("RAZORPAY_SECRET_KEY", "")
        payload = f"{body.razorpay_order_id}|{body.razorpay_payment_id}"

        generated_signature = hmac.new(
            key=secret.encode("utf-8"),
            msg=payload.encode("utf-8"),
            digestmod=hashlib.sha256
        ).hexdigest()

        # 2. Compare signatures
        if generated_signature != body.razorpay_signature:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment Verification Failed"
            )

        # 3. Find payment record in MongoDB (Beanie)
        payment = await Payment.find_one(Payment.order_id == body.razorpay_order_id)

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment Not Found"
            )

        # 4. Update status and payment ID
        payment.status = PaymentStatus.PAID
        payment.payment_id = body.razorpay_payment_id
        await payment.save()

        # 5. Call Auth Service via HTTPX
        async with httpx.AsyncClient() as client:
            auth_response = await client.put(
                f"{AUTH_SERVICE_URL.rstrip('/')}/auth/update-payment",
                json={
                    "userId": payment.user_id,
                    "plan": payment.plan,
                    "credits": payment.credits
                },
                timeout=10.0
            )

            if auth_response.status_code == 200:
                auth_data = auth_response.json()
                print(f"🎉 Payment Verified Successfully: {auth_data}")
                return {
                    "message": "Payment Verified",
                    "user": auth_data.get("user")
                }
        # 6. Return response
        return {"message": "Payment Verified"}

    except HTTPException:
        raise
    except Exception as error:
        print(f"❌ Error verifying payment: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"verify payment error {str(error)}"
        )