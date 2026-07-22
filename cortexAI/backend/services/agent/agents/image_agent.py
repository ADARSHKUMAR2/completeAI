import time
import httpx
from urllib.parse import quote
from config.llmModels import get_model
from utils.upload_AWS import upload_to_s3
from utils.getFrom_AWS import get_from_s3
from graph.state import AgentState
from rich import print

async def image_node(state: AgentState) -> dict:
    """
    Node for the specialized text-to-image workflow.
    """
    print("🎨 Image Generation Agent triggered!")
    
    # 1. Get model instance
    llm = get_model("image")
    
    # 2. Format system prompt with incoming user prompt
    prompt_text = f"""You are an elite AI image prompt engineer.

Convert the user request into a highly detailed image generation prompt.

Requirements:

- Cinematic lighting
- Professional composition
- Ultra realistic
- High detail
- Beautiful color palette
- Sharp focus
- 8K quality
- Photorealism
- Depth of field
- Professional photography
- Stunning visuals

Return only the image prompt.

User Request:
{state.get("prompt", "")}
"""

    # 3. Invoke LLM asynchronously
    res = await llm.ainvoke(prompt_text)
    prompt = res.content.strip() if hasattr(res, "content") else str(res).strip()

    # 4. Construct Pollinations URL with URL-encoded prompt
    image_url = f"https://image.pollinations.ai/prompt/{quote(prompt)}"

    # 5. Fetch image bytes asynchronously
    async with httpx.AsyncClient(timeout=60.0) as client:
        image_res = await client.get(image_url)
        buffer = image_res.content

    # 6. Generate filename using timestamp
    filename = f"image-{int(time.time() * 1000)}.png"

    # 7. Call synchronous S3 functions WITHOUT 'await'
    upload_to_s3(filename, buffer, "image/png")
    download_url = get_from_s3(filename, 60 * 60)

    # 8. Return updated state dictionary
    return {
        **state,
        "aiResponse": f"""# 🖼️ Image Generated Successfully

![Generated Image]({download_url})

💾 [Download Image]({download_url})

⌛ Link expires in 24 hours.""",
        "images": [download_url]
    }