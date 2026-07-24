from graph.state import AgentState
import base64
import os
import aiofiles
from langchain_core.messages import SystemMessage, HumanMessage
from config.llmModels import get_model  # Your LLM loader module
from utils.deductCredits import deduct_credits
from config.agentLimit import check_agent_limit

async def imageAnalyser_node(state: AgentState) -> dict:
    """
    Executes standard conversational queries using the designated 
    chat model engine and updates the graph's AI response state.
    """

    await check_agent_limit(state.get("userId"), state.get("agent"))
    file_info = state.get("file")
    
    if not file_info or not file_info.get("path"):
        return {
            **state,
            "aiResponse": "No image file provided for analysis."
        }

    file_path = file_info.get("path")
    mimetype = file_info.get("mimetype", "image/png")

    try:
        # 1. Fetch configured vision model
        llm = get_model("imageAnalyser")

        # 2. Asynchronously read file and encode to base64
        async with aiofiles.open(file_path, "rb") as image_file:
            content = await image_file.read()
            base64_image = base64.b64encode(content).decode("utf-8")

        # 3. System prompt persona and rules
        system_prompt = """You are CortexAI image analyzer Agent.

Rules:

- Analyze only the uploaded image.
- Answer the user's question accurately.
- If text exists in the image, extract it.
- If charts or tables exist, explain them.
- If something is unclear, say so.
- Use Markdown when helpful.
- Do not hallucinate."""

        # 4. Construct LangChain multimodal human message format
        prompt_text = state.get("prompt") or "analyze the image"
        
        image_data_url = f"data:{mimetype};base64,{base64_image}"

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(
                content=[
                    {
                        "type": "text", 
                        "text": str(prompt_text)
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_data_url
                        }
                    }
                ]
            )
        ]

        # 5. Invoke the LLM model
        response = await llm.ainvoke(messages)

        # 6. Deduct credits upon successful invocation
        user_id = state.get("userId")
        agent_type = state.get("agent", "imageAnalyser")
        if user_id:
            await deduct_credits(user_id, agent_type)

        return {
            **state,
            "aiResponse": response.content
        }

    except Exception as error:
        print(f"❌ Image Analyzer execution failure: {error}")
        return {
            **state,
            "aiResponse": "Failed to analyze file"
        }

    finally:
        # 7. Cleanup temp file on local disk (equivalent to fs.unlink)
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"🧹 Temporary file cleaned up: {file_path}")
            except Exception as cleanup_error:
                print(f"⚠️ Warning: Could not remove temp file: {cleanup_error}")