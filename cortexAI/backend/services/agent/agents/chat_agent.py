from graph.state import AgentState
from config.llmModels import get_model
from config.memory import get_memory
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from pprint import pprint
from rich import print
import json
from datetime import datetime

async def chat_node(state: AgentState) -> dict:
    """
    Executes standard conversational queries using the designated 
    chat model engine and updates the graph's AI response state.
    """
    # 1. Fetch the configured chat model (Groq)
    llm = get_model("chat")
    
    search_results = state.get("search_results") or state.get("searchResults")

    if search_results:
        search_context = (
            f"\n=== LIVE WEB SEARCH RESULTS ===\n"
            f"{json.dumps(search_results, indent=2)}\n"
            f"===============================\n\n"
            f"STRICT SEARCH RULES:\n"
            f"1. You MUST use the LIVE WEB SEARCH RESULTS above to answer the user.\n"
            f"2. The search results contain factual real-time information. Do NOT state that an event has not occurred if results show it has.\n"
            f"3. Do NOT mention internal tools, JSON, or Tavily in your response."
        )
    else:
        search_context = ""

    current_date_str = datetime.now().strftime('%B %d, %Y')
    # 2. Define the agent system persona instructions
    system_prompt = f"""
    You are CortexAI, an intelligent AI assistant. 
    Current Date: {current_date_str}\n

    {search_context}

    If searchContext exists:
    - Use the search results to answer the user's question.
    - Do not mention internal tools.

    Rules:

    - For simple questions, greetings, and short queries, respond naturally in plain text.
    - For technical, educational, coding, or detailed topics, use clean Markdown.

    Formatting:
    
    - Use # for titles and ## for sections.

    - Leave a blank line after headings.

    - Use bullet points for lists.

    - Use numbered lists for steps.

    - Use fenced code blocks with language tags for code.

    - Keep paragraphs short and readable.

    - Never write headings and content on the same line.

    - Never generate large walls of text.
"""
    
    conversation_id = state.get("conversationId")

    history = await get_memory(conversation_id) if conversation_id else []

    # 3. Build the payload array utilizing clean message roles
    messages = [
        SystemMessage(content=system_prompt)
    ]

    if history:
        for msg in history:
            role = msg.get("role")
            content = msg.get("content", "")
            
            if role == "user":
                messages.append(HumanMessage(content=content))
            else:
                messages.append(AIMessage(content=content))

    prompt = state.get("prompt", "")
    messages.append(HumanMessage(content=prompt))

    # print("💬 messages", messages)
    
    print("💬 Chat Agent processing message text...")
    
    try:
        # 4. Invoke the LangChain instance using the synchronous API supported by these models
        response = llm.invoke(messages)
        
        # 5. Return the text update target back into your state schema
        return {"aiResponse": response.content}
        
    except Exception as e:
        print(f"❌ Chat Agent execution failure: {e}")
        return {"aiResponse": "I encountered an issue processing your request."}