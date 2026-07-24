import os
from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
from config.embeddings import embeddings 
from langchain_core.documents import Document
from typing import List

load_dotenv()

async def get_vector_store(docs: List[Document], collection_name: str) -> QdrantVectorStore:
    """
    Connects to an existing Qdrant vector store collection.
    """
    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")  

    vector_store = QdrantVectorStore.from_existing_collection(
        documents=docs,
        embedding=embeddings,
        collection_name=collection_name,
        url=qdrant_url,
        api_key=qdrant_api_key,
    )
    
    return vector_store