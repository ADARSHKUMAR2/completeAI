from graph.state import AgentState
from config.tavily import search_tool

async def search_node(state: AgentState) -> dict:
    """
    Performs live web search queries and returns search results and images.
    """
    print("🔍 Web Search Agent triggered!")
    try:
        prompt = state.get("prompt", "")
        results = await search_tool.ainvoke({"query": prompt})
        
        # Safely extract image URLs and raw text snippets
        extracted_images = []
        raw_results = []

        if isinstance(results, dict):
            extracted_images = results.get("images", [])
            raw_results = results.get("results", [])
        elif isinstance(results, list):
            raw_results = results

        # Clean string image links (filtering out non-string objects)
        clean_images = [str(img) for img in extracted_images if isinstance(img, str)]

        return {
            "search_results": raw_results,  
            "images": clean_images
        }
        
    except Exception as error:
        print(f"❌ Error in Search Agent: {error}")
        return {
            "search_results": [],
            "images": []
        }