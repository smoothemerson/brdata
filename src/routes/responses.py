from pydantic import BaseModel


class ChatResponse(BaseModel):
    answer: str
    # tools_used: list[dict[str, str]]


class ChatRequest(BaseModel):
    question: str


class HealthResponse(BaseModel):
    healthy: bool
