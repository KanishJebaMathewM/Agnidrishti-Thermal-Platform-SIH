import uuid
from datetime import datetime, timezone
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.repositories.event_repository import get_event_by_id
from app.utils.database import get_db

router = APIRouter()


class NotificationLogPayload(BaseModel):
    authority_id: uuid.UUID
    channel: str
    operator_id: str


@router.post("/events/{event_id}/notification-preview")
async def notification_preview(event_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    event = await get_event_by_id(db, event_id)
    if not event: raise HTTPException(404, "Event not found")
    return {"event_id": str(event.id), "classification": event.classification, "severity": event.severity,
            "state": event.state, "district": event.district, "location": {"lat": event.centroid_lat, "lon": event.centroid_lon}}


@router.post("/events/{event_id}/notification-log", status_code=201)
async def notification_log(event_id: uuid.UUID, payload: NotificationLogPayload, db: AsyncSession = Depends(get_db)):
    if not await get_event_by_id(db, event_id): raise HTTPException(404, "Event not found")
    notification = Notification(event_id=event_id, authority_id=payload.authority_id, channel=payload.channel,
                                status="ACTION_TAKEN", operator_id=payload.operator_id,
                                action_taken_at=datetime.now(timezone.utc))
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    return notification