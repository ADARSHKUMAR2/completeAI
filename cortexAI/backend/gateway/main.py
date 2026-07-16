import os
from fastapi import FastAPI
from dotenv import load_dotenv

# 1. Load environment variables from your .env file
load_dotenv()

# 2. Initialize the FastAPI app instance
app = FastAPI()

# 3. Define the port from environment variables (default to 8000 if not found)
PORT = int(os.getenv("PORT", 8000))

# 4. Create the base GET route matching your Express implementation
@app.get("/")
async def root():
    return {"message": "hello from gateway"}

def main():
    print("Hello from gateway!")


if __name__ == "__main__":
    main()
