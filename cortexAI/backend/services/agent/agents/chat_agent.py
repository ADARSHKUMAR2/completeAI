from graph.state import AgentState
from config.llmModels import get_model

async def chat_node(state: AgentState) -> dict:
    """
    Executes standard conversational queries using the designated 
    chat model engine and updates the graph's AI response state.
    """
    # 1. Fetch the configured chat model (Groq)
    llm = get_model("chat")
    
    # 2. Define the agent system persona instructions
    system_prompt = "You are CortexAI, an intelligent AI assistant."
    
    # 3. Build the payload array utilizing clean message roles
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": state.get("prompt", "")}
    ]
    
    print("💬 Chat Agent processing message text...")
    
    try:
        # 4. Asynchronously invoke the LangChain instance
        response = await llm.ainvoke(messages)
        
        # 5. Return the text update target back into your state schema
        return {"aiResponse": response.content}
        
    except Exception as e:
        print(f"❌ Chat Agent execution failure: {e}")
        return {"aiResponse": "I encountered an issue processing your request."}