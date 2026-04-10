from pydantic import BaseModel, Field


class ChatResponse(BaseModel):
    answer: str


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=5000)


class HealthResponse(BaseModel):
    healthy: bool
