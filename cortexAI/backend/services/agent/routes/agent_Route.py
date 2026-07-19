from fastapi import APIRouter
from controllers.agent_Controller import handle_agent_request, AgentRequestPayload

# Initialize the router instance
agent_router = APIRouter()

@agent_router.post("/chat")
async def process_agent_query(payload: AgentRequestPayload):
    """
    Primary ingestion endpoint that executes the multi-agent graph loop.
    """
    return await handle_agent_request(payload)