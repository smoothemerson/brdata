"""MCP tools for IBGE agregados API."""

from mcp_server.ibge_client import IBGEClient


async def get_population(ibge_client: IBGEClient) -> list[dict]:
    """Returns Brazilian population data by state from the most recent IBGE census (aggregate 1705, variable 614)."""
    return await ibge_client.get(
        "/v3/agregados/1705/periodos/-1/variaveis/614",
        params={"localidades": "N3[all]"},
    )


async def search_aggregates(keyword: str, ibge_client: IBGEClient) -> list[dict]:
    """Searches IBGE aggregate tables by keyword in Portuguese (e.g. censo, pib, educacao). Returns matching table metadata including id, nome, and pesquisa fields."""
    results = await ibge_client.get("/v3/agregados", params={"pesquisa": keyword})
    return results[:20]
