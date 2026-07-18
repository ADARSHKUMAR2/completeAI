from datetime import datetime
from pydantic import Field
from beanie import Document

class Conversation(Document):
    title: str = Field(default="New Chat")
    user_id: str  # Maps to your authenticated user's ID
    
    # Beanie handles standard timestamps via default_factory
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "conversations"  # This sets the MongoDB collection name