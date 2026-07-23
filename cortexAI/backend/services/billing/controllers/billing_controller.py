import time
from fastapi import HTTPException, status, Header
from pydantic import BaseModel
from config.Plans import PLANS
from config.razorpay import razorpay_client
from models.paymentModel import Payment, PaymentStatus
import os
import hmac
import hashlib
import httpx

class CreateOrderSchema(BaseModel):
    plan: str

class VerifyPaymentSchema(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://127.0.0.1:8001")

async def create_order(body: CreateOrderSchema, x_user_id: str = Header(None)):
    """
    Creates a new Razorpay payment order and stores initial record in MongoDB.
    """
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing authenticated user header (x-user-id)"
        )

    try:
        plan_key = body.plan.lower()
        selected_plan = PLANS.get(plan_key)

        if not selected_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="plan not found"
            )

        # Create Razorpay order
        order_payload = {
            "amount": int(selected_plan["amount"] * 100),  # Amount in paise
            "currency": "INR",
            "receipt": f"receipt-{int(time.time() * 1000)}"
        }
        order = razorpay_client.order.create(data=order_payload)

        # Create and save Beanie document
        new_payment = Payment(
            userId=x_user_id,
            orderId=order["id"],
            amount=selected_plan["amount"],
            credits=selected_plan["credits"],
            plan=selected_plan["id"],
            currency=order["currency"],
            status=PaymentStatus.CREATED
        )
        await new_payment.insert()

        return {
            "order": order,
            "plan": selected_plan
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

        # 5. Call Auth Service via HTTPX (Equivalent to axios.post in JS)
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

            if auth_response.status_code != 200:
                print(f"⚠️ Warning: Auth service returned status {auth_response.status_code}")

        # 6. Return response matching JS { message: "Payment Verified" }
        return {"message": "Payment Verified"}

    except HTTPException:
        raise
    except Exception as error:
        print(f"❌ Error verifying payment: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"verify payment error {str(error)}"
        )

