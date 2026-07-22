from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing import List

class AgentState(TypedDict):
    """
    Defines the shared memory state tracking variables 
    passed between the router and worker agent nodes.
    """
    prompt: str
    aiResponse: str
    agent: str
    conversationId: str
    messages: Annotated[Sequence[BaseMessage], add_messages]
    search_results: List[dict]
    images: List[str]
    artifacts: List[str]