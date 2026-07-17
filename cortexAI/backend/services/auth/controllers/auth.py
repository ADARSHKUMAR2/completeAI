import json
import uuid
from fastapi import APIRouter, HTTPException, Response, status, Cookie
from pydantic import BaseModel
from firebase_admin import auth as firebase_auth
from models.user import User
from shared.redis.redis import redis_client

router = APIRouter()

# 1. Pydantic model representing your req.body validation schema
class LoginRequest(BaseModel):
    token: str

@router.post("/login")
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
    
@router.post("/logout")
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