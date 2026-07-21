import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables (API keys)
load_dotenv()

# 1. Initialize the LLM client instances
# (Note: Standard Groq models include llama3-8b-8192, llama-3.1-70b-versatile, etc.)
groq_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)

gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)

# 2. Dynamic Model Dispatcher (Replicates the switch statement in JS)
def get_model(agent_type: str):
    """
    Returns the designated LangChain LLM instance depending on 
    the targeted graph worker node type.
    """
    match agent_type:
        case "chat":
            return groq_llm
        case "search":
            return groq_llm
        case "coding":
            return gemini_llm
        case _:
            # Default fallback matching the JS switch block
            return groq_llm