from fastapi import APIRouter
from controllers.chat import create_conversation, get_conversations, save_message, get_messages, GetMessagesSchema, SaveMessageSchema, update_conversation, UpdateConversationSchema
from fastapi.params import Depends

router = APIRouter()

@router.post("/")
async def handle_create_conversation(conversation = Depends(create_conversation)):
    return conversation

@router.get("/")
async def handle_get_conversations(conversations = Depends(get_conversations)):
    return conversations

@router.post("/message/save")
async def handle_save_message(body: SaveMessageSchema):
    return await save_message(body)

@router.post("/message/get")
async def handle_get_messages(body: GetMessagesSchema):
    return await get_messages(body)

@router.put("/update")
async def handle_update_conversation(body: UpdateConversationSchema):
    return await update_conversation(body)