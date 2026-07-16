import os
from fastapi import FastAPI, Request, Response
from dotenv import load_dotenv
import httpx
from utils.proxy import register_proxy
from utils.cors import register_cors
import uvicorn

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

# 4. Create the base GET route matching your Express implementation
@app.get("/")
async def root():
    return {"message": "hello from gateway"}

def main():
    print(f"Gateway server booting up on port {PORT}...")
    uvicorn.run("main:app", host="127.0.0.1", port=PORT, reload=True)

if __name__ == "__main__":
    main()
