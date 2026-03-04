from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.routes.health import ServiceStatus, router
from src.db.connection import get_db

test_app = FastAPI()
test_app.include_router(router)


async def mock_get_db():
    yield MagicMock()


test_app.dependency_overrides[get_db] = mock_get_db


def test_health_all_ok():
    statuses = [
        ServiceStatus(name="postgres", ok=True),
        ServiceStatus(name="mcp", ok=True),
        ServiceStatus(name="ollama", ok=True),
        ServiceStatus(name="ibge", ok=True),
    ]
    with (
        patch(
            "src.api.routes.health.check_postgres",
            new=AsyncMock(return_value=statuses[0]),
        ),
        patch(
            "src.api.routes.health.check_mcp",
            new=AsyncMock(return_value=statuses[1]),
        ),
        patch(
            "src.api.routes.health.check_ollama",
            new=AsyncMock(return_value=statuses[2]),
        ),
        patch(
            "src.api.routes.health.check_ibge",
            new=AsyncMock(return_value=statuses[3]),
        ),
    ):
        with TestClient(test_app) as client:
            response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["healthy"] is True
    assert len(data["services"]) == 4
    assert all(s["ok"] for s in data["services"])


def test_health_one_service_down():
    with (
        patch(
            "src.api.routes.health.check_postgres",
            new=AsyncMock(return_value=ServiceStatus(name="postgres", ok=True)),
        ),
        patch(
            "src.api.routes.health.check_mcp",
            new=AsyncMock(
                return_value=ServiceStatus(
                    name="mcp", ok=False, detail="Connection refused"
                )
            ),
        ),
        patch(
            "src.api.routes.health.check_ollama",
            new=AsyncMock(return_value=ServiceStatus(name="ollama", ok=True)),
        ),
        patch(
            "src.api.routes.health.check_ibge",
            new=AsyncMock(return_value=ServiceStatus(name="ibge", ok=True)),
        ),
    ):
        with TestClient(test_app) as client:
            response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["healthy"] is False
    mcp_status = next(s for s in data["services"] if s["name"] == "mcp")
    assert mcp_status["ok"] is False
    assert mcp_status["detail"] == "Connection refused"
