import json
import time
from config.llmModels import get_model
from utils.upload_AWS import upload_to_s3
from utils.getFrom_AWS import get_from_s3
from utils.generatePpt import generate_ppt
from graph.state import AgentState
from rich import print
from utils.deductCredits import deduct_credits
from config.agentLimit import check_agent_limit

async def ppt_node(state: AgentState) -> dict:
    """
    Node for generating structured PowerPoint presentation JSON & .pptx file.
    """
    print("📊 PPT Agent triggered!")

    try:
        # 1. Fetch LLM instance
        llm = get_model("ppt")

        await check_agent_limit(state.get("userId"), state.get("agent"))
        # 2. Format System Prompt
        prompt = f"""You are a professional presentation designer.

Return ONLY valid JSON.

Format:

{{
"title":"",
"subtitle":"",
"slides":[
{{
"title":"",
"points":[
"",
"",
"",
""
]
}}
]
}}

Rules:

- Generate exactly 6 content slides.
- Each slide should have 4-6 concise bullet points.
- No markdown.
- No explanation.
- No code block.
- Return ONLY JSON.

Topic:

{state.get("prompt", "")}"""

        # 3. Invoke LLM asynchronously
        res = await llm.ainvoke(prompt)

        await deduct_credits(state.get("userId"), state.get("agent"))
        
        raw_content = res.content.strip() if hasattr(res, "content") else str(res).strip()

        # Clean potential markdown backticks (```json ... ```)
        if raw_content.startswith("```"):
            lines = raw_content.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            raw_content = "\n".join(lines).strip()

        # 4. Parse JSON
        data = json.loads(raw_content)

        # 5. Generate PPT Bytes
        ppt_buffer = generate_ppt(data)

        # 6. Generate filename using timestamp
        filename = f"presentation-{int(time.time() * 1000)}.pptx"

        # 7. Upload to S3 & Get Presigned URL (Synchronous functions, no await)
        upload_to_s3(filename, ppt_buffer, "application/vnd.openxmlformats-officedocument.presentationml.presentation")
        download_url = get_from_s3(filename, 3600)  # 1 hour expiration

        # 8. Return updated state dictionary
        return {
            **state,
            "ppt_data": data,
            "aiResponse": f"""# 📊 Presentation Generated Successfully

**{data.get('title', 'Presentation')}**

📥 [Download PowerPoint Presentation (.pptx)]({download_url})

_Link expires in 1 hour._"""
        }

    except Exception as error:
        print("❌ Error in ppt_agent:", error)
        return {
            **state,
            "aiResponse": f"❌ Failed to generate presentation: {str(error)}"
        }