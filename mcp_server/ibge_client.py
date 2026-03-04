"""Async HTTP client wrapper for the IBGE public API."""

import httpx


class IBGEClient:
    def __init__(self, base_url: str) -> None:
        self._client = httpx.AsyncClient(base_url=base_url, timeout=30.0)

    async def get(self, path: str, params: dict | None = None) -> dict | list:
        response = await self._client.get(path, params=params)
        response.raise_for_status()
        return response.json()

    async def close(self) -> None:
        await self._client.aclose()


def get_ibge_client(
    base_url: str = "https://servicodados.ibge.gov.br/api",
) -> IBGEClient:
    return IBGEClient(base_url)
