from fastapi import APIRouter
from controllers.billing_controller import create_order, CreateOrderSchema, verify_payment, VerifyPaymentSchema

router = APIRouter()

@router.post("/create-order")
async def handle_create_order(body: CreateOrderSchema):
    return await create_order(body)

@router.post("/verify")
async def handle_verify_payment(body: VerifyPaymentSchema):
    return await verify_payment(body)