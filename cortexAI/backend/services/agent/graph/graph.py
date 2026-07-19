from langgraph.graph import StateGraph, START, END

# 1. Import your shared LangGraph memory state schema
from graph.state import AgentState

# 2. Import the routing condition rule
from graph.router import route_decision

# 3. Import all worker nodes from your agents subfolder
from agents.chat_agent import chat_node
from agents.coding_agent import coding_node
from agents.image_agent import image_node
from agents.pdf_agent import pdf_node
from agents.ppt_agent import ppt_node
from agents.search_agent import search_node

# Initialize workflow bound to your two-key prompt/aiResponse schema
workflow = StateGraph(AgentState)

# Step A: Register all operational Nodes into the Graph landscape
# Note: We include an explicit "router" block if you want it as a node, 
# or you can route straight out of START if the router logic lives in route_decision!
# For a clean supervisory pattern, we'll keep the router block explicit:
from graph.router import router_node
workflow.add_node("router", router_node)

workflow.add_node("chat", chat_node)
workflow.add_node("coding", coding_node)
workflow.add_node("image_gen", image_node)
workflow.add_node("pdf", pdf_node)
workflow.add_node("ppt", ppt_node)
workflow.add_node("search", search_node)

# Step B: Establish static sequence pipelines (Standard Edges)
workflow.add_edge(START, "router")

# As mapped out, search flows directly to chat instead of finishing early
workflow.add_edge("search", "chat")

# All final destinations funnel out to the END terminator node cleanly
workflow.add_edge("chat", END)
workflow.add_edge("coding", END)
workflow.add_edge("image_gen", END)
workflow.add_edge("pdf", END)
workflow.add_edge("ppt", END)

# Step C: Register the Dynamic Supervisor Matrix (Conditional Edges)
workflow.add_conditional_edges(
    "router",
    route_decision,
    {
        "chat": "chat",
        "coding": "coding",
        "image_gen": "image_gen",
        "pdf": "pdf",
        "ppt": "ppt",
        "search": "search"
    }
)

# Compile the structured blueprint into an executable Python system
agent_app = workflow.compile()

# 2. Write it cleanly in a simple one-liner block
# with open("graph/workflow.png", "wb") as f:
#     f.write(agent_app.graph.png())