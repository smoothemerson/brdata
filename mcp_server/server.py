"""MCP Server for IBGE data access."""

import uvicorn
from fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

mcp = FastMCP("ibge-mcp-server")


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
