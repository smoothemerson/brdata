from mcp_server.ibge_client import IBGEClient


async def get_states(ibge_client: IBGEClient):
    response = await ibge_client.get("/v1/localidades/estados")
    return response


async def get_municipalities(uf: str, ibge_client: IBGEClient):
    uf = uf.upper()
    response = await ibge_client.get(f"/v1/localidades/estados/{uf}/municipios")
    return response
