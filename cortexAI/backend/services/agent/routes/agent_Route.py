from fastapi import APIRouter, Header, HTTPException, status
from controllers.agent_Controller import handle_agent_request, AgentRequestPayload
from typing import Optional

# Initialize the router instance
agent_router = APIRouter()

@agent_router.post("/chat")
async def process_agent_query(payload: AgentRequestPayload,
                              x_user_id: Optional[str] = Header(None, alias="x-user-id")):
    """
    Primary ingestion endpoint that executes the multi-agent graph loop.
    """

    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing authenticated user header (x-user-id)"
        )

    # 2. Pass x_user_id down into controller execution
    return await handle_agent_request(payload, x_user_id=x_user_id)