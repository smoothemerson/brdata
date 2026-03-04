import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import QueryModel, ToolCallModel


async def save_query(
    db: AsyncSession,
    *,
    question: str,
    session_id: uuid.UUID | None,
    answer: str,
    tools_used: list[dict],
    latency_ms: int,
) -> QueryModel:
    query = QueryModel(
        session_id=session_id,
        question=question,
        answer=answer,
        tools_used=tools_used,
        latency_ms=latency_ms,
    )
    db.add(query)
    await db.flush()

    for tool in tools_used:
        tool_call = ToolCallModel(
            query_id=query.id,
            tool_name=tool.get("tool_name", "unknown"),
            params=tool.get("params", {}),
            result=tool.get("result"),
            error=tool.get("error"),
        )
        db.add(tool_call)

    await db.commit()
    await db.refresh(query)
    return query


async def get_history(
    db: AsyncSession,
    *,
    session_id: uuid.UUID | None = None,
    limit: int = 20,
) -> list[QueryModel]:
    stmt = select(QueryModel).order_by(QueryModel.created_at.desc()).limit(limit)
    if session_id is not None:
        stmt = stmt.where(QueryModel.session_id == session_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())
