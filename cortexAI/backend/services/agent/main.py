import os
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv
from config.db import connect_db  # We will update/create this next
from routes.agent_Route import agent_router
from shared.redis.redis import init_redis

# 1. Load environment variables
load_dotenv()
PORT = int(os.getenv("PORT", 8003)) # Typically agents run on a new port like 8003

# 2. Replicate the app.listen callback using FastAPI lifespan context
@asynccontextmanager
async def lifespan(app: FastAPI):
    # This block executes BEFORE the server starts taking requests
    print(f"🤖 agent started at {PORT}")
    await connect_db()
    await init_redis()
    yield
    # Any necessary cleanup code on shutdown goes here

# 3. Instantiate the FastAPI app
app = FastAPI(lifespan=lifespan)

app.include_router(agent_router,prefix="/agent", tags=["agent"])

# 4. Root fallback endpoint (Matches app.get("/") in your image)
@app.get("/")
async def root():
    return {"message": "hello from agent"}

def main():
    uvicorn.run("main:app", host="127.0.0.1", port=PORT, reload=True)

if __name__ == "__main__":
    main()