import os
import httpx

async def get_messages(conversation_id: str):
    # Extract the chat service URL from environment variables (with fallback)
    chat_service = os.getenv("CHAT_SERVICE", "http://127.0.0.1:8002")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{chat_service}/chat/message/get/{conversation_id}")
            response.raise_for_status()
            return response.json()  
    except Exception as error:
        print(f"Error fetching messages: {error}")
        return None