from pydantic import BaseModel
from typing import Dict


class PlanDetails(BaseModel):
    id: str
    name: str
    amount: int
    credits: int
    validity: int = 30  # Default 30 days


PLANS: Dict[str, PlanDetails] = {
    "free": PlanDetails(
        id="free",
        name="Free",
        amount=0,
        credits=100,
        validity=30
    ),
    "starter": PlanDetails(
        id="starter",
        name="Starter",
        amount=199,
        credits=500,
        validity=30
    ),
    "pro": PlanDetails(
        id="pro",
        name="Pro",
        amount=499,
        credits=1000,
        validity=30
    ),
}