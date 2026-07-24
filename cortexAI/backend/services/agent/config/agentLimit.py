import math
from shared.redis.redis import redis_client  

LIMITS = {
    "chat": 2,
    "coding": 5,
    "pdf": 5,
    "ppt": 5,
    "image": 5,
    "search": 5
}

class RateLimitException(Exception):
    def __init__(self, status: int, data: dict):
        self.status = status
        self.data = data
        super().__init__(data.get("message"))


async def check_agent_limit(user_id: str, agent: str) -> dict:
    max_limit = LIMITS.get(agent, LIMITS["chat"])
    key = f"rate:{user_id}:{agent}"
    
    count = await redis_client.incr(key)

    if count == 1:
        await redis_client.expire(key, 60)

    ttl = await redis_client.ttl(key)

    if count > max_limit:
        minutes = math.floor(ttl / 60)
        seconds = ttl % 60
        time_str = f"{minutes}m : {seconds}s" if minutes > 0 else f"{seconds}s"

        error_data = {
            "success": False,
            "agent": agent,
            "limit": max_limit,
            "remainingTime": ttl,
            "retryAfter": time_str,
            "message": f"You have reached the {agent} limit ({max_limit} requests/minute). Try again in {time_str}."
        }
        
        raise RateLimitException(status=429, data=error_data)

    return {
        "remaining": max(0, max_limit - count),
        "limit": max_limit
    }