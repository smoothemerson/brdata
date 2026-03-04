import asyncio

import httpx
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.db.connection import get_db

router = APIRouter()


class ServiceStatus(BaseModel):
    name: str
    ok: bool
    detail: str | None = None


class HealthResponse(BaseModel):
    healthy: bool
    services: list[ServiceStatus]


async def check_postgres(db: AsyncSession) -> ServiceStatus:
    try:
        await db.execute(text("SELECT 1"))
        return ServiceStatus(name="postgres", ok=True)
    except Exception as e:
        return ServiceStatus(name="postgres", ok=False, detail=str(e))


async def check_mcp() -> ServiceStatus:
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{settings.mcp_base_url}/health", timeout=5)
            r.raise_for_status()
        return ServiceStatus(name="mcp", ok=True)
    except Exception as e:
        return ServiceStatus(name="mcp", ok=False, detail=str(e))


async def check_ollama() -> ServiceStatus:
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{settings.ollama_base_url}/api/tags", timeout=5)
            r.raise_for_status()
        return ServiceStatus(name="ollama", ok=True)
    except Exception as e:
        return ServiceStatus(name="ollama", ok=False, detail=str(e))


async def check_ibge() -> ServiceStatus:
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{settings.ibge_base_url}/v1/localidades/estados", timeout=5
            )
            r.raise_for_status()
        return ServiceStatus(name="ibge", ok=True)
    except Exception as e:
        return ServiceStatus(name="ibge", ok=False, detail=str(e))


@router.get("/health", response_model=HealthResponse)
async def health(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    results = await asyncio.gather(
        check_postgres(db),
        check_mcp(),
        check_ollama(),
        check_ibge(),
        return_exceptions=True,
    )
    names = ["postgres", "mcp", "ollama", "ibge"]
    services = []
    for name, result in zip(names, results):
        if isinstance(result, Exception):
            services.append(ServiceStatus(name=name, ok=False, detail=str(result)))
        else:
            services.append(result)
    healthy = all(s.ok for s in services)
    return HealthResponse(healthy=healthy, services=services)
