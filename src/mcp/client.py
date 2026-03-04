import asyncio

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient

from src.config import settings

_tools_cache: list | None = None
_lock = asyncio.Lock()


async def load_mcp_tools() -> list[BaseTool]:
    global _tools_cache
    async with _lock:
        if _tools_cache is not None:
            return _tools_cache
        try:
            client = MultiServerMCPClient(
                {
                    "ibge": {
                        "url": f"{settings.mcp_base_url}/mcp",
                        "transport": "streamable_http",
                    }
                }
            )
            _tools_cache = await client.get_tools()
            return _tools_cache
        except Exception as e:
            raise RuntimeError(f"MCP server unavailable: {e}") from e
