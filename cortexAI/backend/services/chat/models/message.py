from enum import Enum
from datetime import datetime
from pydantic import Field
from beanie import Document, PydanticObjectId, Link
from models.conversation import Conversation
from pydantic import Field, ConfigDict
from typing import List, Optional

class ChatRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Message(Document):
    # Option A: Direct ID reference (Simpler, standard for microservices)
    conversation_id: PydanticObjectId = Field(..., alias="conversationId")
    
    # Option B: DB Ref Link (Uncomment if you want Beanie to automatically fetch the conversation object)
    # conversation_id: Link[Conversation]
    
    role: ChatRole
    content: str
    images: Optional[List[str]] = []
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

    class Settings:
        name = "messages"  # This sets the MongoDB collection name