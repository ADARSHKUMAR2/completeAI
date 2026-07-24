import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

# Reads GEMINI_API_KEY or GOOGLE_API_KEY from environment variables automatically
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001"
)