from langchain_mcp_adapters.client import MultiServerMCPClient

from src.env import MCP_BASE_URL


async def load_mcp_tools():
    client = MultiServerMCPClient(
        {
            "ibge-mcp-server": {
                "transport": "streamable_http",
                "url": MCP_BASE_URL,
            }
        }
    )

    tools = await client.get_tools()

    return tools
