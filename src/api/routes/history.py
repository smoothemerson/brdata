import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas import HistoryItem
from src.db.connection import get_db
from src.db.repository import get_history

router = APIRouter()


@router.get("/history", response_model=list[HistoryItem])
async def get_history_route(
    session_id: str | None = Query(default=None),
    limit: int = Query(default=20, le=100),
    db: AsyncSession = Depends(get_db),
) -> list[HistoryItem]:
    sid = uuid.UUID(session_id) if session_id else None
    rows = await get_history(db, session_id=sid, limit=limit)
    return [
        HistoryItem(
            query_id=str(row.id),
            session_id=str(row.session_id) if row.session_id else None,
            question=row.question,
            answer=row.answer,
            tools_used=row.tools_used,
            latency_ms=row.latency_ms,
            created_at=row.created_at,
        )
        for row in rows
    ]
