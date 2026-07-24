import json
from config.llmModels import get_model
from graph.state import AgentState
from utils.getFrom_AWS import get_from_s3
from utils.upload_AWS import upload_to_s3
from utils.generatePdf import generate_pdf
from rich import print
import time
from utils.deductCredits import deduct_credits
from config.agentLimit import check_agent_limit

async def pdf_node(state: AgentState) -> dict:
    """
    Placeholder node for parsing, analyzing, and querying PDF document contents.
    """
    print("📄 PDF Agent triggered!")
    
    try:
        # 1. Fetch LLM instance
        llm = get_model("pdf")

        await check_agent_limit(state.get("userId"), state.get("agent"))

        # 2. Format system prompt
        prompt = f"""You are an expert document writer.

Return ONLY valid JSON.

Do NOT return markdown.

Do NOT return explanations.

Structure:

{{
"title":"",
"subtitle":"",
"sections":[
{{
"heading":"",
"points":[]
}}
]
}}

Generate 4-8 sections.

Each section should have 3-6 concise bullet points.

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

        # 4. Parse JSON content
        data = json.loads(raw_content)

        # 5. Generate PDF bytes using reportlab helper
        pdf_buffer = generate_pdf(data)

        # 6. Generate filename using timestamp
        filename = f"pdf-{int(time.time() * 1000)}.pdf"

        # 7. Upload to S3 & Get Presigned URL (Synchronous functions, no await)
        upload_to_s3(filename, pdf_buffer, "application/pdf")
        download_url = get_from_s3(filename, 3600)  # 1 hour expiration

        # 8. Return updated state dictionary
        return {
            **state,
            "pdf_data": data,
            "aiResponse": f"""# 📄 PDF Generated

**{data.get('title', 'Untitled Document')}**

📨 [Download PDF]({download_url})

_Link expires in 1 hour._"""
        }

    except Exception as error:
        print("❌ Error in pdf_agent:", error)
        return {
            **state,
            "aiResponse": f"❌ Failed to generate PDF: {str(error)}"
        }