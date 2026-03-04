"""Unit tests for nomes MCP tools."""

from unittest.mock import AsyncMock

import pytest

from mcp_server.tools.nomes import get_name_frequency


NAME_FIXTURE = [
    {
        "nome": "JOSE",
        "sexo": None,
        "localidade": "BR",
        "res": [
            {"periodo": "1930[", "frequencia": 127245},
            {"periodo": "[1930,1940[", "frequencia": 249786},
        ],
    }
]


@pytest.fixture
def mock_client():
    client = AsyncMock()
    return client


async def test_get_name_frequency_uppercases_name(mock_client):
    mock_client.get.return_value = NAME_FIXTURE

    result = await get_name_frequency("jose", mock_client)

    mock_client.get.assert_called_once_with("/v2/censos/nomes/JOSE")
    assert isinstance(result, list)
    assert result[0]["nome"] == "JOSE"


async def test_get_name_frequency_lowercase_input(mock_client):
    mock_client.get.return_value = NAME_FIXTURE

    await get_name_frequency("maria", mock_client)

    mock_client.get.assert_called_once_with("/v2/censos/nomes/MARIA")


async def test_get_name_frequency_already_uppercase(mock_client):
    mock_client.get.return_value = NAME_FIXTURE

    await get_name_frequency("ANA", mock_client)

    mock_client.get.assert_called_once_with("/v2/censos/nomes/ANA")
