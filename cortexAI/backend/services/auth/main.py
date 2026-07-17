import os
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv
from config.db import connect_db
from config.firebase import init_firebase
from controllers.auth import router as auth_router
from pathlib import Path
import sys
from shared.redis.redis import init_redis

# 1. Load environment variables
load_dotenv()
PORT = int(os.getenv("PORT", 8001))

# 2. Define the lifespan context manager (Replaces Express's app.listen callback logic)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # This code runs BEFORE the server starts taking requests
    print(f"auth started at {PORT}")
    await connect_db()
    await init_redis()
    init_firebase()
    
    yield  # The application runs while paused here
    
    # Any code written here runs AFTER the server shuts down (Cleanups go here)

# 3. Pass the lifespan to the FastAPI instance
app = FastAPI(lifespan=lifespan)

# 2. Register the router (equivalent to app.use("/auth", authRouter) in Express)
# We can include a prefix here so all routes inside that file automatically get it!
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

@app.get("/")
async def root():
    return {"message": "hello from auth"}

def main():
    uvicorn.run("main:app", host="127.0.0.1", port=PORT, reload=True)

if __name__ == "__main__":
    main()