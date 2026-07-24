from graph.state import AgentState
import os
import time
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.messages import SystemMessage, HumanMessage
from config.llmModels import get_model
from config.vectorDb import get_vector_store
from utils.deductCredits import deduct_credits

async def pdfRag_node(state: AgentState) -> dict:
    """
    Executes standard conversational queries using the designated 
    chat model engine and updates the graph's AI response state.
    """

    file_info = state.get("file")
    
    if not file_info or not file_info.get("path"):
        return {
            **state,
            "aiResponse": "No PDF file provided for processing."
        }

    file_path = file_info.get("path")

    try:
        # 1. Parse PDF and extract pages/text
        loader = PyPDFLoader(file_path)
        pages = await loader.aload()  # Asynchronously load PDF pages

        # 2. Split PDF text into chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        docs = splitter.split_documents(pages)

        # 3. Store chunks in Qdrant with a unique collection name
        timestamp_ms = int(time.time() * 1000)
        collection_name = f"pdf-{timestamp_ms}"
        
        vector_store = await get_vector_store(docs, collection_name)

        # 4. Perform similarity search using user's prompt
        prompt_text = state.get("prompt") or "Summarize the document"
        relevant_docs = await vector_store.asimilarity_search(prompt_text, k=5)

        # 5. Extract and join context from relevant documents
        context = "\n\n".join([doc.page_content for doc in relevant_docs])

        # 6. Load LLM and construct system/human messages
        llm = get_model("pdfRAG")

        system_prompt = """You are CortexAI PDF Assistant.

Rules:

- Answer ONLY from the uploaded PDF.
- Never make up information.
- If the answer is not present in the PDF, reply:
"I couldn't find this information in the uploaded PDF."
- Use Markdown formatting."""

        user_content = f"Context:\n{context}\n\nQuestion:\n{prompt_text}"

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_content)
        ]

        # 7. Invoke the model
        response = await llm.ainvoke(messages)

        # 8. Deduct user credits upon success
        user_id = state.get("userId")
        agent_type = state.get("agent", "pdfRAG")
        if user_id:
            await deduct_credits(user_id, agent_type)

        return {
            **state,
            "aiResponse": response.content
        }

    except Exception as error:
        print(f"❌ PDF RAG execution failure: {error}")
        return {
            **state,
            "aiResponse": "Failed to analyze PDF file"
        }

    finally:
        # 9. Cleanup temporary file from local disk
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"🧹 Temporary PDF removed: {file_path}")
            except Exception as cleanup_err:
                print(f"⚠️ Warning: Could not remove temp file: {cleanup_err}")

