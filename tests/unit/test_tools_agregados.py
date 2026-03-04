"""Unit tests for agregados MCP tools."""

from unittest.mock import AsyncMock

import pytest

from mcp_server.tools.agregados import (
    get_aggregate_data,
    get_population,
    search_aggregates,
)


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


AGGREGATES_FIXTURE = [
    {"id": str(i), "nome": f"Table {i}", "pesquisa": "censo"} for i in range(25)
]


async def test_search_aggregates_passes_keyword_as_query_param(mock_client):
    mock_client.get.return_value = AGGREGATES_FIXTURE

    await search_aggregates("censo", mock_client)

    mock_client.get.assert_called_once_with(
        "/v3/agregados", params={"pesquisa": "censo"}
    )


async def test_search_aggregates_truncates_to_20_results(mock_client):
    mock_client.get.return_value = AGGREGATES_FIXTURE

    result = await search_aggregates("censo", mock_client)

    assert len(result) == 20


async def test_search_aggregates_returns_fewer_than_20_when_small_response(mock_client):
    mock_client.get.return_value = AGGREGATES_FIXTURE[:5]

    result = await search_aggregates("pib", mock_client)

    assert len(result) == 5


AGGREGATE_DATA_FIXTURE = [
    {
        "id": 9514,
        "variavel": "Rendimento médio",
        "unidade": "Reais",
        "resultados": [],
    }
]


async def test_get_aggregate_data_constructs_correct_url(mock_client):
    mock_client.get.return_value = AGGREGATE_DATA_FIXTURE

    result = await get_aggregate_data(9514, "2022", 1, mock_client)

    mock_client.get.assert_called_once_with(
        "/v3/agregados/9514/periodos/2022/variaveis/1"
    )
    assert result == AGGREGATE_DATA_FIXTURE


async def test_get_aggregate_data_uses_latest_period(mock_client):
    mock_client.get.return_value = AGGREGATE_DATA_FIXTURE

    await get_aggregate_data(1705, "-1", 614, mock_client)

    mock_client.get.assert_called_once_with(
        "/v3/agregados/1705/periodos/-1/variaveis/614"
    )
