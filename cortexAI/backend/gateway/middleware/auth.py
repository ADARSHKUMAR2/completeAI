import json
from fastapi import HTTPException, status, Cookie
from shared.redis.redis import redis_client

async def protect(session: str = Cookie(None)):
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="unauthorized"
        )

    session_data_raw = await redis_client.get(f"session-{session}")

    if not session_data_raw:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="session expired"
        )

    try:
        user_data = json.loads(session_data_raw)
        return user_data

    except (json.JSONDecodeError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Session parsing failure"
        )