import os
import redis.asyncio as aioredis

# 1. Initialize the Redis client instance (Equivalent to: new Redis(process.env.REDIS_URL))
# decode_responses=True ensures you get strings back instead of raw byte strings (b"value")
redis_client = aioredis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379"),
    decode_responses=True
)

# 2. Connection health-check helper (Equivalent to: redis.on("connect", ...))
async def init_redis():
    try:
        # ping() acts as a handshake check to see if Redis is actually up and running
        await redis_client.ping()
        print("🚀 Redis connected successfully")
    except Exception as e:
        print(f"❌ Failed to connect to Redis: {str(e)}")