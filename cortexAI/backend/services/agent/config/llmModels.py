import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openrouter import ChatOpenRouter
from enum import StrEnum

# Load environment variables (API keys)
load_dotenv()

class AgentType(StrEnum):
    CHAT = "chat"
    SEARCH = "search"
    CODING = "coding"
    IMAGE_ANALYSER = "imageAnalyser"
    IMAGE_ANALYSIS = "imageAnalyser"
    PDF_RAG= "pdfRag"

# 1. Initialize the LLM client instances
# (Note: Standard Groq models include llama3-8b-8192, llama-3.1-70b-versatile, etc.)
groq_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)

gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    convert_system_message_to_human=True
)

openrouter_llm = ChatOpenRouter(
    model="deepseek/deepseek-chat",
    temperature=0,
    max_tokens=2500,
    max_retries=2,
    # other params...
)

# 2. Dynamic Model Dispatcher (Replicates the switch statement in JS)
def get_model(agent_type: str):
    """
    Returns the designated LangChain LLM instance depending on 
    the targeted graph worker node type.
    """
    if isinstance(agent_type, str):
        try:
            agent_type = AgentType(agent_type)
        except ValueError:
            pass  # Will hit default case in match statement

    match agent_type:
        case AgentType.CHAT | AgentType.SEARCH:
            return groq_llm
        case AgentType.CODING:
            return gemini_llm
        case AgentType.IMAGE_ANALYSER | AgentType.IMAGE_ANALYSIS:
            return gemini_llm
        case AgentType.PDF_RAG:
            return gemini_llm
        case _:
            return groq_llm