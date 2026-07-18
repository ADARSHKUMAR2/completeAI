from enum import Enum
from datetime import datetime
from pydantic import Field
from beanie import Document, PydanticObjectId, Link
from conversation import Conversation

class ChatRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Message(Document):
    # Option A: Direct ID reference (Simpler, standard for microservices)
    # conversation_id: PydanticObjectId 
    
    # Option B: DB Ref Link (Uncomment if you want Beanie to automatically fetch the conversation object)
    conversation_id: Link[Conversation]
    
    role: ChatRole
    content: str
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "messages"  # This sets the MongoDB collection name