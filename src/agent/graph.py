from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode
from langchain_ollama import ChatOllama

from src.agent.nodes import (
    make_agent_node,
    make_tool_node_with_tracking,
    should_continue,
)
from src.agent.state import AgentState
from src.config import settings
from src.mcp.client import load_mcp_tools

_graph_cache = None


async def build_graph():
    tools = await load_mcp_tools()

    llm = ChatOllama(model=settings.ollama_model, base_url=settings.ollama_base_url)
    llm_with_tools = llm.bind_tools(tools)

    tool_node = ToolNode(tools)

    agent_fn = make_agent_node(llm_with_tools)
    tracking_tool_fn = make_tool_node_with_tracking(tool_node)

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_fn)
    graph.add_node("tools", tracking_tool_fn)

    graph.add_edge(START, "agent")
    graph.add_conditional_edges(
        "agent", should_continue, {"tools": "tools", "__end__": END}
    )
    graph.add_edge("tools", "agent")

    return graph.compile()


async def get_graph():
    global _graph_cache
    if _graph_cache is None:
        _graph_cache = await build_graph()
    return _graph_cache
