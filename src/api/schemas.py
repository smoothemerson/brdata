from datetime import datetime

from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    answer: str
    tools_used: list[dict]
    latency_ms: int
    query_id: str


class HistoryItem(BaseModel):
    query_id: str
    session_id: str | None
    question: str
    answer: str | None
    tools_used: list[dict] | None
    latency_ms: int | None
    created_at: datetime
