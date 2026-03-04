"""MCP tools for IBGE localidades API."""

from mcp_server.ibge_client import IBGEClient


async def get_states(ibge_client: IBGEClient) -> list[dict]:
    """Returns all 27 Brazilian states with their region information."""
    return await ibge_client.get("/v1/localidades/estados")


async def get_municipalities(uf: str, ibge_client: IBGEClient) -> list[dict]:
    """Returns all municipalities for a Brazilian state.

    uf must be a 2-letter state code (e.g. SP, RJ, MG).
    """
    uf = uf.upper()
    return await ibge_client.get(f"/v1/localidades/estados/{uf}/municipios")
