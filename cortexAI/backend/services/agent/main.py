import os
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from config.db import connect_db  # We will update/create this next
from routes.agent_Route import agent_router
from shared.redis.redis import init_redis
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from config.agentLimit import RateLimitException

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

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print("❌ 422 Validation Error Details:", exc.errors())
    return JSONResponse(status_code=422, content={"detail": exc.errors()})

@app.exception_handler(Exception)
async def global_error_handler(request: Request, err: Exception):
    print(f"❌ Centralized Error Handler Caught: {err}")

    if isinstance(err, RateLimitException):
        return JSONResponse(
            status_code=err.status,
            content=err.data
        )

    # Fallback 500 server error response
    return JSONResponse(
        status_code=500,
        content={"message": f"agent error {str(err)}"}
    )

app.include_router(agent_router,prefix="/agent", tags=["agent"])

# 4. Root fallback endpoint (Matches app.get("/") in your image)
@app.get("/")
async def root():
    return {"message": "hello from agent"}

def main():
    uvicorn.run("main:app", host="127.0.0.1", port=PORT, reload=True)

if __name__ == "__main__":
    main()