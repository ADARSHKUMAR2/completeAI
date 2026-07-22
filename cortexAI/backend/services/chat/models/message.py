from enum import Enum
from datetime import datetime
from pydantic import Field
from beanie import Document, PydanticObjectId, Link
from models.conversation import Conversation
from pydantic import Field, ConfigDict
from typing import List, Optional
from pydantic import BaseModel

class ChatRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class FileSchema(BaseModel):
    name: str
    content: str

# Equivalent to artifactSchema (_id: false)
class ArtifactSchema(BaseModel):
    id: int
    type: str
    files: List[FileSchema] = Field(default_factory=list)

class Message(Document):
    # Option A: Direct ID reference (Simpler, standard for microservices)
    conversation_id: PydanticObjectId = Field(..., alias="conversationId")
    
    # Option B: DB Ref Link (Uncomment if you want Beanie to automatically fetch the conversation object)
    # conversation_id: Link[Conversation]
    
    role: ChatRole
    content: str
    images: Optional[List[str]] = Field(default_factory=list)
    artifacts: Optional[List[ArtifactSchema]] = Field(default_factory=list)
    
    created_at: datetime = Field(default_factory=datetime.utcnow, alias="createdAt")
    updated_at: datetime = Field(default_factory=datetime.utcnow, alias="updatedAt")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

    class Settings:
        name = "messages"  # This sets the MongoDB collection name