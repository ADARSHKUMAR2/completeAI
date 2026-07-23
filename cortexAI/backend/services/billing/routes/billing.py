from fastapi import APIRouter, Header, HTTPException, status
from controllers.billing_controller import create_order, CreateOrderSchema, verify_payment, VerifyPaymentSchema

router = APIRouter()

@router.post("/create-order")
async def handle_create_order(
    body: CreateOrderSchema, 
    x_user_id: str = Header(None, alias="x-user-id")
):
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: User ID header missing"
        )
    return await create_order(body, user_id=x_user_id)

@router.post("/verify")
async def handle_verify_payment(body: VerifyPaymentSchema):
    return await verify_payment(body)