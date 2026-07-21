from fastapi import HTTPException, status, Header
from models.conversation import Conversation
from typing import List
from pydantic import BaseModel
from beanie import PydanticObjectId
from typing import Optional
from models.message import ChatRole, Message

class SaveMessageSchema(BaseModel):
    conversationId: PydanticObjectId
    role: ChatRole
    content: str
    images: Optional[List[str]]

class GetMessagesSchema(BaseModel):
    conversationId: PydanticObjectId

class UpdateConversationSchema(BaseModel):
    id: PydanticObjectId
    title: str

async def create_conversation(x_user_id: str = Header(None)):
    """
    Creates a new chat conversation workspace for the authenticated user.
    """
    # 1. Check if the gateway passed the header successfully
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing authenticated user header (x-user-id)"
        )
        
    try:
        print(f"userId: {x_user_id}")
        
        # 2. Instantiate and save the new conversation document to MongoDB
        # Beanie's .insert() is equivalent to Mongoose's .create()
        new_conversation = Conversation(user_id=x_user_id)
        await new_conversation.insert()
        
        # 3. Return the database document as a clean JSON dictionary response
        return new_conversation
        
    except Exception as error:
        print(f"❌ Error creating conversation: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"create conversation error {str(error)}"
        )
    
async def get_conversations(x_user_id: str = Header(None)) -> List[Conversation]:
    """
    Retrieves all chat conversations for the user, sorted by most recently updated.
    """
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing authenticated user header (x-user-id)"
        )
        
    try:
        print(f"userId: {x_user_id}")
        
        # 1. Find all docs matching user_id and sort them
        # Mongoose: Conversation.find({ userId }).sort({ updatedAt: -1 })
        # Beanie: .find() returns a query object, we chain .sort() with a minus sign (-) for descending order
        conversations = await Conversation.find(
            Conversation.user_id == x_user_id
        ).sort("-updated_at").to_list()
        
        return conversations
        
    except Exception as error:
        print(f"❌ Error fetching conversations: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"get conversation error {str(error)}"
        )
    
async def save_message(body: SaveMessageSchema) -> Message:
    """
    Saves a new chat message into a specific conversation workspace.
    """
    try:
        # Instantiate and save into MongoDB (Mongoose: Message.create)
        new_message = Message(
            conversation_id=PydanticObjectId(body.conversationId),
            role=body.role,
            content=body.content,
            images=body.images or []
        )
        await new_message.insert()
        return new_message
        
    except Exception as error:
        print(f"❌ Error saving message: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"save message error {str(error)}"
        )

async def get_messages(conversation_id: str) -> List[Message]:
    """
    Retrieves all messages for a specific conversation, ordered newest first.
    """
    try:
        messages = await Message.find(
            Message.conversation_id == PydanticObjectId(conversation_id)
        ).to_list()
        
        return messages
        
    except Exception as error:
        print(f"❌ Error retrieving messages: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"get messages error {str(error)}"
        )
   
async def update_conversation(body: UpdateConversationSchema) -> Conversation:
    try:
        # Find document by ID and apply $set directly
        conversation = await Conversation.get(PydanticObjectId(body.id))
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Performs atomic update directly in DB and syncs Python model
        await conversation.set({Conversation.title: body.title})
        
        return conversation
        
    except HTTPException:
        raise
    except Exception as error:
        print(f"❌ Error updating conversation: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"update conversation error {str(error)}"
        )