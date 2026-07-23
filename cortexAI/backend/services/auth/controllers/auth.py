import json
import uuid
from fastapi import HTTPException, Response, status, Cookie
from pydantic import BaseModel
from firebase_admin import auth as firebase_auth
from models.user import User
from shared.redis.redis import redis_client
from beanie import PydanticObjectId
from datetime import datetime, timedelta, timezone
from typing import Optional

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
        user_id_str = str(user.id)
        ttl_seconds = 7 * 24 * 60 * 60 # 7 days * 24 hours * 60 minutes * 60 seconds = 604800 seconds

        # Save User-to-Session mapping 
        await redis_client.set(
            f"user-session-{user_id_str}",
            json.dumps({"sessionId": session_id}),
            ex=ttl_seconds
        )

        # 2. Serialize user data to JSON format
        user_session_data = {
            "userId": str(user.id), # Assuming MongoDB ObjectId, cast to string
            "name": user.name,
            "email": user.email,
            "avatar": user.avatar,
            "plan": user.plan,
            "credits": user.credits,
            "totalCredits": user.total_credits,
            "planExpiresAt": user.plan_expires_at.isoformat() if user.plan_expires_at else None
        }
        
        
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
    
async def update_user_payment(body: UpdateUserPaymentSchema, session: Optional[str] = Cookie(None)):
    """
    Updates the user's plan, adds credits, sets plan expiration date (+30 days),
    and updates active session data in Redis.
    """
    try:
        # 1. Find user by ID
        user = (
            await User.get(PydanticObjectId(body.userId))
            if PydanticObjectId.is_valid(body.userId)
            else await User.find_one(User.id == body.userId)
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # 2. Accumulate plan and credits
        user.plan = body.plan
        user.credits = (user.credits or 0) + body.credits
        user.total_credits = (user.total_credits or 0) + body.credits
        user.plan_expires_at = datetime.now(timezone.utc) + timedelta(days=30)
        user.updated_at = datetime.now(timezone.utc)

        # 3. Save MongoDB Document
        await user.save()

        # 4. Fetch User-to-Session mapping
        user_id_str = str(user.id)
        session_data_raw = await redis_client.get(f"user-session-{user_id_str}")

        session_id = None
        if session_data_raw:
            try:
                # Decode bytes to string if needed
                if isinstance(session_data_raw, bytes):
                    session_data_raw = session_data_raw.decode("utf-8")

                session_info = json.loads(session_data_raw)
                if isinstance(session_info, dict):
                    session_id = session_info.get("sessionId")
                else:
                    session_id = str(session_info)
            except Exception:
                session_id = str(session_data_raw)

        # 5. Overwrite Active Session Cache in Redis
        if session_id:
            updated_session_data = {
                "userId": user_id_str,
                "name": getattr(user, "name", ""),
                "email": user.email,
                "avatar": getattr(user, "avatar", None),
                "plan": user.plan,
                "credits": user.credits,
                "totalCredits": user.total_credits,
                "planExpiresAt": user.plan_expires_at.isoformat() if user.plan_expires_at else None
            }

            ttl_seconds = 7 * 24 * 60 * 60  # 7 days
            await redis_client.set(
                f"session-{session_id}",
                json.dumps(updated_session_data),
                ex=ttl_seconds
            )
            print(f"✅ Redis session-{session_id} updated successfully!")
        else:
            print(f"⚠️ Warning: Could not locate active session_id for user {user_id_str}")

        # 6. Return payload
        return {
            "success": True,
            "message": "User payment details updated successfully",
            "user": {
                "userId": user_id_str,
                "name": getattr(user, "name", ""),
                "email": user.email,
                "avatar": getattr(user, "avatar", None),
                "plan": user.plan,
                "credits": user.credits,
                "totalCredits": user.total_credits,
                "planExpiresAt": user.plan_expires_at.isoformat() if user.plan_expires_at else None
            }
        }

    except HTTPException:
        raise
    except Exception as error:
        print(f"❌ Error updating user payment: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"update user payment error {str(error)}"
        )