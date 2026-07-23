from datetime import datetime
from typing import Optional
from beanie import Document, Indexed
from pydantic import Field

# This class definition combines your schema definition (lines 3-13)
# and the model compilation (line 15) into a single step.
class User(Document):
    firebase_uid: str = Indexed(unique=True)
    name: Optional[str] = None
    email: Optional[str] = None
    avatar: Optional[str] = None
    plan: str = "free"
    credits: int = 100
    total_credits: int = Field(default=100, alias="totalCredits")
    plan_expires_at: Optional[datetime] = Field(default=None, alias="planExpiresAt")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"

