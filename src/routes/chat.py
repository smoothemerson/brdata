from fastapi import APIRouter, Depends

from src.agent.agent import agent_call
from src.routes.responses import ChatRequest, ChatResponse
from src.security import verify_api_key

router = APIRouter()


@router.post("/chat", response_model=ChatResponse, summary="Chat with the AI assistant")
async def chat(request: ChatRequest, _: None = Depends(verify_api_key)):
    question = request.question
    answer = await agent_call(question)

    return ChatResponse(
        answer=answer,
    )
