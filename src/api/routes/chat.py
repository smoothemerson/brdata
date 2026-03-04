import time
import uuid

from fastapi import APIRouter, Depends
from langchain_core.messages import HumanMessage
from sqlalchemy.ext.asyncio import AsyncSession

from src.agent.graph import get_graph
from src.api.schemas import ChatRequest, ChatResponse
from src.db.connection import get_db
from src.db.repository import save_query

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest, db: AsyncSession = Depends(get_db)
) -> ChatResponse:
    graph = await get_graph()

    session_id = uuid.UUID(request.session_id) if request.session_id else None

    start_time = time.monotonic()
    result = await graph.ainvoke(
        {
            "messages": [HumanMessage(content=request.question)],
            "question": request.question,
            "session_id": request.session_id,
            "tools_called": [],
        }
    )
    latency_ms = int((time.monotonic() - start_time) * 1000)

    answer = result["messages"][-1].content
    tools_used = result.get("tools_called", [])

    saved = await save_query(
        db,
        question=request.question,
        session_id=session_id,
        answer=answer,
        tools_used=tools_used,
        latency_ms=latency_ms,
    )

    return ChatResponse(
        answer=answer,
        tools_used=tools_used,
        latency_ms=latency_ms,
        query_id=str(saved.id),
    )
