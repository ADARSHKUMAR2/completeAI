from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

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