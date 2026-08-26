from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from redis.asyncio import Redis
from sqlalchemy import text

from app.config import settings
from app.utils.database import async_session

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@router.get("/ready")
async def ready() -> dict[str, str]:
    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        redis = Redis.from_url(settings.redis_url)
        await redis.ping()
        await redis.aclose()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Service dependencies are unavailable") from exc
    return {"status": "ready"}
