import json
import redis.asyncio as redis
from utils.getMessages import get_messages
import os
from dotenv import load_dotenv

# Initialize async Redis client (adjust host/port/env as needed)
# redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# 1. Load variables from .env file into environment
load_dotenv()

# 2. Get the REDIS_URL with a fallback default
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# 3. Create the shared Redis client connection
redis_client = redis.from_url(
    REDIS_URL,
    decode_responses=True # Automatically decodes byte responses to Python strings
)

async def add_message(conversation_id: str, role: str, content: str):
    key = f"messages-{conversation_id}"
    
    raw_messages = await redis_client.get(key)
    messages = json.loads(raw_messages) if raw_messages else []
    
    # Append new message
    messages.append({
        "role": role,
        "content": content
    })
    
    # Maintain sliding window of max 20 messages
    if len(messages) > 20:
        messages.pop(0)  
        
    await redis_client.set(key, json.dumps(messages))

async def get_memory(conversation_id: str):
    key = f"messages-{conversation_id}"
    
    # Check cache first
    cached = await redis_client.get(key)
    if cached:
        return json.loads(cached)
    
    # Fetch from DB/Microservice if cache miss occurs
    messages = await get_messages(conversation_id)
    
    if messages is not None:
        # Cache in Redis with 24-hour Expiration (EX in seconds: 24 * 60 * 60 = 86400)
        await redis_client.set(key, json.dumps(messages), ex=24 * 60 * 60)
        
    return messages