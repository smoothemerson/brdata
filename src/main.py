from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.mcp.client import load_mcp_tools
from src.routes.chat import router as chat_router
from src.routes.health import router as health_router
from src.tracking.setup import mlflow_autolog


@asynccontextmanager
async def lifespan(app: FastAPI):
    mlflow_autolog()
    await load_mcp_tools()
    yield


app = FastAPI(
    title="BRData",
    description="A data assistant for Brazilian public data",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(chat_router)
app.include_router(health_router)
