"""Unit tests for agregados MCP tools."""

from unittest.mock import AsyncMock

import pytest

from mcp_server.tools.agregados import get_population


POPULATION_FIXTURE = [
    {
        "id": 614,
        "variavel": "População residente",
        "unidade": "Pessoas",
        "resultados": [
            {
                "classificacoes": [],
                "series": [
                    {
                        "localidade": {
                            "id": "35",
                            "nivel": {"id": "N3", "nome": "Estado"},
                            "nome": "São Paulo",
                        },
                        "serie": {"2022": "44411238"},
                    }
                ],
            }
        ],
    }
]


@pytest.fixture
def mock_client():
    client = AsyncMock()
    return client


async def test_get_population_returns_list(mock_client):
    mock_client.get.return_value = POPULATION_FIXTURE

    result = await get_population(mock_client)

    mock_client.get.assert_called_once_with(
        "/v3/agregados/1705/periodos/-1/variaveis/614",
        params={"localidades": "N3[all]"},
    )
    assert isinstance(result, list)
    assert result[0]["id"] == 614


async def test_get_population_passes_correct_params(mock_client):
    mock_client.get.return_value = POPULATION_FIXTURE

    await get_population(mock_client)

    _, kwargs = mock_client.get.call_args
    assert kwargs["params"]["localidades"] == "N3[all]"
