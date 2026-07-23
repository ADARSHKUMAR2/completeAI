import os
from fastapi import FastAPI, Request, Response, Depends
from dotenv import load_dotenv
import httpx
from utils.proxy import register_proxy, register_proxy_with_header
from utils.cors import register_cors
import uvicorn
from middleware.auth import protect
from controllers.user import get_current_user

# 1. Load environment variables from your .env file
load_dotenv()

# 2. Initialize the FastAPI app instance
app = FastAPI()

# 3. Define the port from environment variables (default to 8000 if not found)
PORT = int(os.getenv("PORT", 8000))

register_cors(app)

register_proxy(
    app, 
    path_prefix="/auth", 
    target_url=os.getenv("AUTH_SERVICE_URL", "http://127.0.0.1:8001")
)

register_proxy_with_header(
    app,
    path_prefix="/chat",
    target_url=os.getenv("CHAT_SERVICE_URL", "http://127.0.0.1:8002")
)

register_proxy_with_header(
    app,
    path_prefix="/agent",
    target_url=os.getenv("AGENT_SERVICE_URL", "http://127.0.0.1:8003")
)

register_proxy_with_header(
    app,
    path_prefix="/billing",
    target_url=os.getenv("BILLING_SERVICE_URL", "http://127.0.0.1:8004")
)

# Register the protected validation endpoint
@app.get("/me")
async def check_me(user_data: dict = Depends(protect)):
    print(f"👤 Current user: {user_data}")
    # 1. 'Depends(protect)' runs first to parse the cookie and verify the session in Redis.
    # 2. If it succeeds, it feeds 'user_data' right into our controller function below.
    return await get_current_user(user_data)

# 4. Create the base GET route matching your Express implementation
@app.get("/")
async def root():
    return {"message": "hello from gateway"}

def main():
    print(f"Gateway server booting up on port {PORT}...")
    uvicorn.run("main:app", host="127.0.0.1", port=PORT, reload=True)

if __name__ == "__main__":
    main()
