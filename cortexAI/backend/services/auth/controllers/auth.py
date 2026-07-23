import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

from beanie import PydanticObjectId
from fastapi import Cookie, HTTPException, Response, status
from firebase_admin import auth as firebase_auth
from pydantic import BaseModel

from models.user import User
from shared.redis.redis import redis_client

# ------------------------------------------------------------------------------
# Schemas & Constants
# ------------------------------------------------------------------------------

class LoginRequest(BaseModel):
    token: str


class UpdateUserPaymentSchema(BaseModel):
    plan: str
    credits: int
    userId: str


class DeductCreditsSchema(BaseModel):
    userId: str
    agent: str


COST = {
    "chat": 1,
    "search": 5,
    "coding": 10,
    "pdf": 10,
    "ppt": 10,
    "image": 10,
}

TTL_SEVEN_DAYS = 7 * 24 * 60 * 60  # 604,800 seconds

# ------------------------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------------------------

async def _get_user_by_id(user_id: str) -> Optional[User]:
    """Helper to fetch a user safely by ObjectId string or raw string ID."""
    if PydanticObjectId.is_valid(user_id):
        return await User.get(PydanticObjectId(user_id))
    return await User.find_one(User.id == user_id)


def _build_user_session_dict(user: User) -> dict:
    """Standardizes user session data serialization for Redis & API payloads."""
    plan_expires = getattr(user, "plan_expires_at", None)
    return {
        "userId": str(user.id),
        "name": getattr(user, "name", "") or "",
        "email": user.email,
        "avatar": getattr(user, "avatar", None),
        "plan": getattr(user, "plan", "free"),
        "credits": getattr(user, "credits", 0),
        "totalCredits": getattr(user, "total_credits", 100),
        "planExpiresAt": plan_expires.isoformat() if plan_expires else None,
    }


async def _resolve_active_session_id(user_id_str: str) -> Optional[str]:
    """Retrieves and parses the active session ID mapped to a user from Redis."""
    raw_data = await redis_client.get(f"user-session-{user_id_str}")
    if not raw_data:
        return None

    if isinstance(raw_data, bytes):
        raw_data = raw_data.decode("utf-8")

    try:
        parsed = json.loads(raw_data)
        if isinstance(parsed, dict):
            return parsed.get("sessionId")
        return str(parsed)
    except Exception:
        return str(raw_data)


async def _update_redis_session(user: User) -> bool:
    """Refreshes active Redis session cache for a user with updated model attributes."""
    user_id_str = str(user.id)
    session_id = await _resolve_active_session_id(user_id_str)

    if session_id:
        session_data = _build_user_session_dict(user)
        await redis_client.set(
            f"session-{session_id}",
            json.dumps(session_data),
            ex=TTL_SEVEN_DAYS
        )
        return True

    print(f"⚠️ Warning: Could not resolve active session_id for user {user_id_str}")
    return False

# ------------------------------------------------------------------------------
# Controllers
# ------------------------------------------------------------------------------

async def login(payload: LoginRequest, response: Response):
    try:
        # 1. Verify Firebase token
        decoded_token = firebase_auth.verify_id_token(payload.token)
        firebase_uid = decoded_token.get("uid")
        email = decoded_token.get("email")
        name = decoded_token.get("name", "")

        # 2. Get or create user
        user = await User.find_one(User.firebase_uid == firebase_uid)
        if not user:
            user = User(firebase_uid=firebase_uid, email=email, name=name)
            await user.insert()
            print(f"🎉 Created a new user record for: {email}")

        # 3. Create unique session IDs
        session_id = str(uuid.uuid4())
        user_id_str = str(user.id)

        # 4. Write dual-mapping to Redis
        user_session_payload = json.dumps({"sessionId": session_id})
        session_data_payload = json.dumps(_build_user_session_dict(user))

        await redis_client.set(
            f"user-session-{user_id_str}",
            user_session_payload,
            ex=TTL_SEVEN_DAYS
        )
        await redis_client.set(
            f"session-{session_id}",
            session_data_payload,
            ex=TTL_SEVEN_DAYS
        )

        # 5. Set session cookie
        response.set_cookie(
            key="session",
            value=session_id,
            httponly=True,
            secure=False,  # Set to True in production HTTPS environments
            samesite="strict",
            max_age=TTL_SEVEN_DAYS
        )

        return user

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login error: {str(error)}"
        )


async def logout(response: Response, session: Optional[str] = Cookie(None)):
    try:
        if session:
            await redis_client.delete(f"session-{session}")

        response.delete_cookie(
            key="session",
            httponly=True,
            samesite="strict"
        )
        return {"message": "logout successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"logout error: {str(e)}"
        )


async def update_user_payment(body: UpdateUserPaymentSchema):
    try:
        user = await _get_user_by_id(body.userId)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Update attributes
        now = datetime.now(timezone.utc)
        user.plan = body.plan
        user.credits = (user.credits or 0) + body.credits
        user.total_credits = (user.total_credits or 0) + body.credits
        user.plan_expires_at = now + timedelta(days=30)
        user.updated_at = now

        await user.save()

        # Update Redis cache using helper
        await _update_redis_session(user)

        return {
            "success": True,
            "message": "User payment details updated successfully",
            "user": _build_user_session_dict(user)
        }

    except HTTPException:
        raise
    except Exception as error:
        print(f"❌ Error updating user payment: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"update user payment error: {str(error)}"
        )


async def deduct_credits(body: DeductCreditsSchema):
    try:
        user = await _get_user_by_id(body.userId)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user not found"
            )

        agent = body.agent.lower()
        required_credits = COST.get(agent, 1)

        if (user.credits or 0) < required_credits:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not enough credits."
            )

        # Deduct credits & save
        user.credits -= required_credits
        user.updated_at = datetime.now(timezone.utc)
        await user.save()

        # Sync updated credits to Redis session
        await _update_redis_session(user)

        return {
            "success": True,
            "credits": user.credits,
            "requiredCredits": required_credits
        }

    except HTTPException:
        raise
    except Exception as error:
        print(f"❌ Error deducting credits: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"deduct credits error: {str(error)}"
        )