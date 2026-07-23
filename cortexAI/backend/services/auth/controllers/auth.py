import json
import uuid
from fastapi import HTTPException, Response, status, Cookie
from pydantic import BaseModel
from firebase_admin import auth as firebase_auth
from models.user import User
from shared.redis.redis import redis_client
from beanie import PydanticObjectId
from datetime import datetime, timedelta


# 1. Pydantic model representing your req.body validation schema
class LoginRequest(BaseModel):
    token: str

class UpdateUserPaymentSchema(BaseModel):
    plan: str
    credits: int
    userId: str

async def login(payload: LoginRequest, response: Response):
    try:
        # 2. Verify incoming frontend client ID token 
        decoded_token = firebase_auth.verify_id_token(payload.token)
        firebase_uid = decoded_token.get("uid")
        email = decoded_token.get("email")
        name = decoded_token.get("name", "")

        # 3. Query the user via Beanie using the decoded UID (Lines 9-11 in JS)
        user = await User.find_one(User.firebase_uid == firebase_uid)
        
        if not user:
            user = User(
                firebase_uid=firebase_uid,
                email=email,
                name=name
                # Add any other initial registration fields your user model requires
            )
            await user.insert()
            print(f"🎉 Created a new user record for: {email}")

        # 4. Generate a unique session ID (crypto.randomUUID() parallel)
        session_id = str(uuid.uuid4())

        # 2. Serialize user data to JSON format
        user_session_data = {
            "userId": str(user.id), # Assuming MongoDB ObjectId, cast to string
            "name": user.name,
            "email": user.email,
            "avatar": user.avatar
        }
        
        # 3. Save to Redis with a 7-day expiration (Equivalent to: redis.set(..., "EX", ...))
        # 7 days * 24 hours * 60 minutes * 60 seconds = 604800 seconds
        ttl_seconds = 7 * 24 * 60 * 60 
        
        await redis_client.set(
            f"session-{session_id}", 
            json.dumps(user_session_data), 
            ex=ttl_seconds
        )

        # 5. Attach the HTTP-only cookie (res.cookie(...) parallel)
        # Note: max_age in Python takes seconds (7 days = 7 * 24 * 60 * 60)
        response.set_cookie(
            key="session",
            value=session_id,
            httponly=True,
            secure=False,  # Set to True when running in production HTTPS environments
            samesite="strict",
            max_age=7 * 24 * 60 * 60
        )

        # 6. Return user payload. FastAPI sets the status to 200 OK by default
        return user

    except Exception as error:
        # Matches your catch (error) block
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login error: {str(error)}"
        )
    
async def logout(response: Response, session: str = Cookie(None)):
    try:
        # 1. Check if the session cookie even exists (Equivalent to: req.cookies?.session)
        if session:
            # 2. Obliterate the key-value store entry inside Redis (Equivalent to: redis.del)
            await redis_client.delete(f"session-{session}")
        
        # 3. Tell the user's browser to destroy the tracking cookie (Equivalent to: res.clearCookie)
        # Note: Pass the exact same path/domain configurations if custom parameters were used on login
        response.delete_cookie(
            key="session",
            httponly=True,
            samesite="strict"
        )
        
        return {"message": "logout successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"logout error {str(e)}"
        )

async def update_user_payment(body: UpdateUserPaymentSchema, session: str = Cookie(None)):
    """
    Updates the user's plan, adds credits, and sets plan expiration date (30 days from now).
    and updates the active session data stored in Redis.
    """
    try:
        # 1. Find user by ID (handles both MongoDB ObjectId and string IDs)
        user = await User.get(PydanticObjectId(body.userId)) if PydanticObjectId.is_valid(body.userId) else await User.find_one(User.id == body.userId)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # 2. Update plan and accumulate credits
        user.plan = body.plan
        user.credits += body.credits
        user.total_credits += body.credits

        # 3. Set plan expiration date (+30 days)
        user.plan_expires_at = datetime.utcnow() + timedelta(days=30)

        # 4. Save updated document
        await user.save()

        if session:
            updated_session_data = {
                "userId": str(user.id),
                "name": user.name,
                "email": user.email,
                "avatar": user.avatar,
                "plan": user.plan,
                "credits": user.credits,
                "totalCredits": user.total_credits,
                "planExpiresAt": user.plan_expires_at.isoformat() if user.plan_expires_at else None
            }

            ttl_seconds = 7 * 24 * 60 * 60  # 7 days
            await redis_client.set(
                f"session-{session}",
                json.dumps(updated_session_data),
                ex=ttl_seconds
            )

        # 6. Return response matching JS { success: true } format
        return {"success": True}

        return {
            "message": "User payment details updated successfully",
            "user": user
        }

    except HTTPException:
        raise
    except Exception as error:
        print(f"❌ Error updating user payment: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"update user payment error {str(error)}"
        )