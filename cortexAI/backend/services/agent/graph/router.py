from pydantic import BaseModel, Field
from typing import Literal
from graph.state import AgentState
from config.llmModels import get_model

class RouterDecision(BaseModel):
    selected_agent: Literal["chat", "search", "coding", "pdf", "ppt", "image_gen"] = Field(
        description="The target specialized worker agent selected to handle the user query."
    )

async def router_node(state: AgentState) -> dict:
    """
    Analyzes the incoming prompt using an LLM and structured tools, 
    then updates the state memory with the routed destination.
    """
    # Fetch the model mapped specifically for the supervisor gateway
    base_llm = get_model("chat")
    
    # Force the LLM to strictly output our Pydantic structural format
    structured_llm = base_llm.with_structured_output(RouterDecision)
    
    # Formulate the system prompt instructions from your reference images
    system_prompt = (
        "You are an agent router.\n\n"
        "Available agents:\n"
        "- chat\n- search\n- coding\n- pdf\n- ppt\n- image_gen\n\n"
        "Rules:\n"
        "chat: General conversation, explanations, learning, questions.\n"
        "search: Current events, latest information, news, recent developments, internet lookup.\n"
        "coding: Generate code, debug code, build projects, architecture, API design.\n"
        "pdf: Questions about generate PDFs or document context.\n"
        "ppt: Questions about generate ppts or ppt context.\n"
        "image_gen: Questions about generating images or visual graphic creation.\n"
    )
    
    # Package into LangChain message components
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"User Query: {state.get('prompt', '')}"}
    ]
    
    print(f"🔮 Router evaluating: '{state.get('prompt', '')}'")
    
    try:
        # Run the LLM structured query invocation using the compatible synchronous API
        decision: RouterDecision = structured_llm.invoke(messages)
        print(f"🎯 Router picked: {decision.selected_agent}")
        
        # Return the update back to the LangGraph dictionary state
        return {"agent": decision.selected_agent}
        
    except Exception as e:
        print(f"⚠️ Router evaluation failed: {e}. Defaulting to 'chat'.")
        return {"agent": "chat"}

def route_decision(state: AgentState) -> str:
    """
    Pipes the flow configuration map out of the router step.
    """
    # Temporary fallback so it defaults to a regular chat node for safety
    # selected_agent = state.get("agent", "chat")
    
    # # Standardize the mapping keys to match our graph layout node registrations
    # if selected_agent == "imageGen":
    #     return "image_gen"
        
    # return selected_agent

    return state.get("agent", "chat")