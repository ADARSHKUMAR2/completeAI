from fastapi import APIRouter, Cookie, Response
from typing import Optional

from controllers.auth import (
    LoginRequest,
    UpdateUserPaymentSchema,
    DeductCreditsSchema,
    login,
    logout,
    update_user_payment,
    deduct_credits
)

router = APIRouter()


@router.post("/login")
async def handle_login(payload: LoginRequest, response: Response):
    return await login(payload, response)


@router.post("/logout")
async def handle_logout(response: Response, session: Optional[str] = Cookie(None)):
    return await logout(response, session)


@router.put("/update-payment")
async def handle_update_user_payment(body: UpdateUserPaymentSchema):
    return await update_user_payment(body)

@router.post("/deduct-credits")
async def handle_deduct_credits(body: DeductCreditsSchema):
    return await deduct_credits(body)