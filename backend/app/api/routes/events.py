import math
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import event_repository
from app.schemas.event_schemas import EventDetail, EventSummary
from app.schemas.observation_schemas import ObservationDetail
from app.utils.database import get_db

router = APIRouter()


@router.get("", response_model=dict)
async def list_events(page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=200), state: str | None = None,
                      classification: str | None = None, status: str | None = None, anomaly_only: bool = False,
                      from_date: datetime | None = None, to_date: datetime | None = None, db: AsyncSession = Depends(get_db)):
    items, total = await event_repository.get_events(db, limit, (page - 1) * limit, state, classification, status, anomaly_only, from_date, to_date)
    return {"items": [EventSummary.model_validate(item) for item in items], "total": total, "page": page, "pages": math.ceil(total / limit) if total else 0}


async def _event(db: AsyncSession, event_id: uuid.UUID):
    item = await event_repository.get_event_by_id(db, event_id)
    if not item:
        raise HTTPException(404, "Event not found")
    return item


@router.get("/{event_id}", response_model=EventDetail)
async def get_event(event_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await _event(db, event_id)


@router.get("/{event_id}/observations", response_model=list[ObservationDetail])
async def event_observations(event_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    event = await _event(db, event_id)
    return event.observations


@router.get("/{event_id}/timeline", response_model=list[ObservationDetail])
async def event_timeline(event_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    await _event(db, event_id)
    return await event_repository.get_event_timeline(db, event_id)