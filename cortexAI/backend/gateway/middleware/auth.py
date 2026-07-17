import json
from fastapi import Request, HTTPException, status, Cookie
from pathlib import Path
import sys
from shared.redis.redis import redis_client

async def protect(session: str = Cookie(None)):
    # 1. Check if the session cookie even exists (req.cookies?.session)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="unauthorized"
        )
    
    # 2. Grab the session text from Redis (redis.get)
    session_data_raw = await redis_client.get(f"session-{session}")
    
    # 3. Handle a missing or naturally expired session cache key
    if not session_data_raw:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="session expired"
        )
    
    try:
        # 4. Parse JSON string into a Python dict (JSON.parse)
        user_data = json.loads(session_data_raw)
        
        # Return the user dictionary context to any protected route that requests it
        return user_data
        
    except (json.JSONDecodeError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Session parsing failure"
        )