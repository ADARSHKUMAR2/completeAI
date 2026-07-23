import httpx
import os

async def deduct_credits(user_id: str, agent: str) -> dict | None:
    """
    Calls the API Gateway to deduct user credits.
    """

    auth_service_url = os.getenv("AUTH_SERVICE_URL", "http://127.0.0.1:8001")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{auth_service_url}/auth/deduct-credits",
                json={"userId": user_id, "agent": agent},
                timeout=10.0,
            )

            response.raise_for_status()

            data = response.json()
            print(f"💳 Credit Deduction Response: {data}")
            return data

    except httpx.HTTPStatusError as err:
        print(f"❌ API Error ({err.response.status_code}): {err.response.text}")
        return None
    except Exception as err:
        print(f"❌ Network Error: {err}")
        return None