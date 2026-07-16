import uuid
from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel
from firebase_admin import auth as firebase_auth
from models.user import User

router = APIRouter()

# 1. Pydantic model representing your req.body validation schema
class LoginRequest(BaseModel):
    token: str

@router.post("/login")
async def login(payload: LoginRequest, response: Response):
    try:
        # 2. Verify incoming frontend client ID token (Lines 7-8 in JS)
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