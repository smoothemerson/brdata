"""MCP tools for IBGE name frequency data."""

from mcp_server.ibge_client import IBGEClient


async def get_name_frequency(name: str, ibge_client: IBGEClient) -> list[dict]:
    """Returns frequency distribution of a Brazilian first name across census decades.

    name: a single first name in Portuguese (e.g. JOSE, MARIA, ANA). Case-insensitive.
    """
    return await ibge_client.get(f"/v2/censos/nomes/{name.upper()}")
