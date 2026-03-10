from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from src.mcp.client import load_mcp_tools
from src.routes.chat import router as chat_router
from src.routes.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await load_mcp_tools()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(chat_router)
app.include_router(health_router)

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
