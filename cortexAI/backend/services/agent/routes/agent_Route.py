from fastapi import APIRouter, Header, HTTPException, status, Request, File, UploadFile
from controllers.agent_Controller import handle_agent_request, AgentRequestPayload
from typing import Optional

agent_router = APIRouter()

@agent_router.post("/chat")
async def process_agent_query(
    request: Request,
    x_user_id: Optional[str] = Header(None, alias="x-user-id")
):
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing authenticated user header (x-user-id)"
        )

    # Parse incoming multipart form data directly from request
    form_data = await request.form()
    
    prompt = form_data.get("prompt", "")
    conversation_id = form_data.get("conversationId", "")
    agent = form_data.get("agent", "auto")
    file_val = form_data.get("file", None)

    file = file_val if hasattr(file_val, "filename") and file_val.filename else None

    payload = AgentRequestPayload(
        prompt=prompt,
        conversationId=conversation_id,
        agent=agent
    )

    return await handle_agent_request(payload, x_user_id=x_user_id, file=file)