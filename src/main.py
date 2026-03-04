from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.agent.graph import get_graph
from src.api.routes.chat import router as chat_router
from src.api.routes.history import router as history_router
from src.db.connection import engine
from src.db.models import Base
from src.mcp.client import load_mcp_tools


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await load_mcp_tools()
    await get_graph()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(chat_router)
app.include_router(history_router)


@app.get("/")
async def root():
    return {"status": "ok"}
