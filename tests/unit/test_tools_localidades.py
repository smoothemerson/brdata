"""Unit tests for localidades MCP tools."""

from unittest.mock import AsyncMock

import pytest

from mcp_server.tools.localidades import get_municipalities, get_states


STATES_FIXTURE = [
    {
        "id": 35,
        "sigla": "SP",
        "nome": "São Paulo",
        "regiao": {"id": 3, "sigla": "SE", "nome": "Sudeste"},
    },
    {
        "id": 33,
        "sigla": "RJ",
        "nome": "Rio de Janeiro",
        "regiao": {"id": 3, "sigla": "SE", "nome": "Sudeste"},
    },
]

MUNICIPALITIES_FIXTURE = [
    {"id": 3550308, "nome": "São Paulo"},
    {"id": 3509502, "nome": "Campinas"},
]


@pytest.fixture
def mock_client():
    client = AsyncMock()
    return client


async def test_get_states_returns_list_with_sigla(mock_client):
    mock_client.get.return_value = STATES_FIXTURE

    result = await get_states(mock_client)

    mock_client.get.assert_called_once_with("/v1/localidades/estados")
    assert isinstance(result, list)
    assert result[0]["sigla"] == "SP"


async def test_get_municipalities_uppercases_uf(mock_client):
    mock_client.get.return_value = MUNICIPALITIES_FIXTURE

    result = await get_municipalities("sp", mock_client)

    mock_client.get.assert_called_once_with("/v1/localidades/estados/SP/municipios")
    assert isinstance(result, list)
    assert result[0]["nome"] == "São Paulo"


async def test_get_municipalities_already_uppercase(mock_client):
    mock_client.get.return_value = MUNICIPALITIES_FIXTURE

    await get_municipalities("RJ", mock_client)

    mock_client.get.assert_called_once_with("/v1/localidades/estados/RJ/municipios")
