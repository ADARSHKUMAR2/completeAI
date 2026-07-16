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
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"

# In Python, there is NO NEED to write "export default User". 
# Any other file can now simply run: from models.user import User