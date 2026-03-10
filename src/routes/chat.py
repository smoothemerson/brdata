from fastapi import APIRouter

from src.agent.agent import agent_call
from src.routes.responses import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    question = request.question

    answer = await agent_call(question)

    return ChatResponse(
        answer=answer,
    )
