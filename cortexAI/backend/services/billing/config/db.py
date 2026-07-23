import os
from pymongo import AsyncMongoClient
from beanie import init_beanie

from models.paymentModel import Payment


async def connect_db():
    try:
        mongodb_uri = os.getenv("MONGODB_URI")

        if not mongodb_uri:
            raise ValueError("MONGODB_URI environment variable is missing!")

        client = AsyncMongoClient(mongodb_uri)
        db = client["billing"]

        await init_beanie(
            database=db,
            document_models=[Payment],
        )

        print("billing db connected")

    except Exception as error:
        print(f"db error {error}")
        raise