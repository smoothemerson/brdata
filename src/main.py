from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.db.connection import engine
from src.db.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"status": "ok"}
