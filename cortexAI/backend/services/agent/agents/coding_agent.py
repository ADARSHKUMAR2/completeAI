from graph.state import AgentState
from config.llmModels import get_model
from rich import print
import json
import time

async def coding_node(state: AgentState) -> dict:
    """
    Placeholder node for the specialized coding agent workflow.
    """
    print("💻 Coding Agent placeholder triggered!")
    
    intent_llm = get_model("intent")
    
    prompt_text = f"""You are an intent classifier.

Return ONLY one of these values.

CODE_GENERATION
CODE_REVIEW
CODE_EXPLANATION
DEBUGGING
OPTIMIZATION
CONVERSION
DOCUMENTATION

User Request:
{state.get("prompt", "")}
"""

    intent_res = await intent_llm.ainvoke(prompt_text)
    
    # Extract intent string cleanly
    intent = intent_res.content.strip()
    print("Intent classified:", intent)

    coding_llm = get_model("coding")

    if intent == "CODE_GENERATION":
        
        prompt = f"""You are CortexAI Coding Agent.

Generate the requested project.

Default stack:
- HTML
- CSS
- JavaScript

Use React / Next.js / Vue ONLY if explicitly requested.

Rules:
- Responsive
- Modern UI
- CSS Variables
- Flexbox/Grid
- Smooth Scroll
- Hover Effects
- Beautiful spacing
- Single page unless user asks otherwise.

Return ONLY valid JSON.

Schema:
{{
  "files": [
    {{
      "name": "index.html",
      "content": "..."
    }},
    {{
      "name": "style.css",
      "content": "..."
    }},
    {{
      "name": "script.js",
      "content": "..."
    }}
  ]
}}

- Output must start with {{
- Output must end with }}
- No markdown
- No explanation
- No extra text
- No ```
- Never mention intent

User Request:
{state.get("prompt", "")}
"""
        code_res = await coding_llm.ainvoke(prompt)
        
        print ("💻 Code generation response:", json.loads(code_res.content))

        clean_content = code_res.content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(clean_content)

        return {
    "aiResponse": "Code Generated Successfully.",
    "artifacts": [
        {
            "id": int(time.time() * 1000),  # Equivalent to Date.now() in JS (milliseconds)
            "type": "Project",
            "title": state.get("prompt", "New Title"),
            "files": data.get("files", [])   # Safe get with default fallback []
        }
    ]
}
    
    prompt = f"""The user's request is:
{intent}

Return Markdown only.

Never generate project files.

Use headings like:

# Overview

## Explanation

## Problems

## Improvements

## Best Practices

## Optimized Code (if needed)

User Request:
{state.get("prompt", "")}
"""

    res = await coding_llm.ainvoke(prompt)

    return {
        "aiResponse": res.content.strip(),
        "artifacts": []
    }