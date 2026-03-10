from fastapi import APIRouter

from src.routes.responses import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def chat():
    return HealthResponse(
        healthy=True,
    )
