"""MCP Server for IBGE data access."""

import os

import uvicorn
from fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

from mcp_server.ibge_client import get_ibge_client
from mcp_server.tools.localidades import get_municipalities, get_states

mcp = FastMCP("ibge-mcp-server")

_ibge_client = get_ibge_client(
    os.getenv("IBGE_BASE_URL", "https://servicodados.ibge.gov.br/api")
)


@mcp.tool()
async def ibge_get_states() -> list[dict]:
    """Returns all 27 Brazilian states with their region information."""
    return await get_states(_ibge_client)


@mcp.tool()
async def ibge_get_municipalities(uf: str) -> list[dict]:
    """Returns all municipalities for a Brazilian state.

    uf must be a 2-letter state code (e.g. SP, RJ, MG).
    """
    return await get_municipalities(uf, _ibge_client)


async def health(request):
    return JSONResponse({"status": "ok"})


app = Starlette(
    routes=[
        Route("/health", health, methods=["GET"]),
        Mount("/mcp", app=mcp.http_app()),
    ]
)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
