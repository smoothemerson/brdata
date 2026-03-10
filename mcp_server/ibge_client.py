import httpx

from mcp_server.env import IBGE_BASE_URL


class IBGEClient:
    def __init__(self, base_url: str) -> None:
        self._client = httpx.AsyncClient(base_url=base_url, timeout=30.0)

    async def get(self, path: str) -> dict | list:
        response = await self._client.get(path)
        response.raise_for_status()
        return response.json()


def get_ibge_client() -> IBGEClient:
    return IBGEClient(IBGE_BASE_URL)
