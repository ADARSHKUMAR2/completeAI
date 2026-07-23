import os
from pymongo import AsyncMongoClient
from beanie import init_beanie
from models.conversation import Conversation
from models.message import Message

async def connect_db():
    try:
        # 1. Grab the connection string
        mongodb_uri = os.getenv("MONGODB_URI")
        
        if not mongodb_uri:
            raise ValueError("MONGODB_URI environment variable is missing!")
            
        # 2. Use the modern, native AsyncMongoClient instead of Motor
        client = AsyncMongoClient(mongodb_uri)
        
        # 3. Explicitly target your "auth" database name from the URL
        db = client["billing"]
        
        # 4. Initialize Beanie smoothly
        await init_beanie(
            database=db, 
            document_models=[Conversation,Message]  # Put your Beanie Document classes here later
        )
        
        print("billing db connected")
        
    except Exception as error:
        print(f"db error {error}")