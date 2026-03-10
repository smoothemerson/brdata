from fastmcp import FastMCP

from mcp_server.ibge_client import get_ibge_client
from mcp_server.tools.location import get_municipalities, get_states

mcp = FastMCP("ibge-mcp-server")

_ibge_client = get_ibge_client()


@mcp.tool()
async def ibge_get_states():
    """Returns all 27 Brazilian states with their region information."""
    return await get_states(_ibge_client)


@mcp.tool()
async def ibge_get_municipalities(uf: str):
    """Returns all municipalities for a Brazilian state.

    uf must be a 2-letter state code (e.g. SP, RJ, MG).
    """
    return await get_municipalities(uf, _ibge_client)


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8001)
