import uuid
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import OperatorFeedback
from app.repositories.event_repository import get_event_by_id, update_event_classification, update_event_status
from app.utils.database import get_db

router = APIRouter()


class ReviewPayload(BaseModel):
    reviewer: str
    comment: str | None = None


class ReclassifyPayload(ReviewPayload):
    new_classification: str


async def save_feedback(db, event, reviewer, comment, label):
    db.add(OperatorFeedback(event_id=event.id, model_prediction=event.classification,
                            model_confidence=event.classification_confidence, human_label=label,
                            reviewer=reviewer, comment=comment))
    await db.commit()
    await db.refresh(event)
    return event


@router.post("/events/{event_id}/confirm")
async def confirm(event_id: uuid.UUID, payload: ReviewPayload, db: AsyncSession = Depends(get_db)):
    event = await get_event_by_id(db, event_id)
    if not event: raise HTTPException(404, "Event not found")
    await update_event_status(db, event_id, "CONFIRMED")
    return await save_feedback(db, event, payload.reviewer, payload.comment, event.classification)


@router.post("/events/{event_id}/false-alarm")
async def false_alarm(event_id: uuid.UUID, payload: ReviewPayload, db: AsyncSession = Depends(get_db)):
    event = await get_event_by_id(db, event_id)
    if not event: raise HTTPException(404, "Event not found")
    await update_event_status(db, event_id, "FALSE_ALARM")
    return await save_feedback(db, event, payload.reviewer, payload.comment, "FALSE_ALARM")


@router.post("/events/{event_id}/reclassify")
async def reclassify(event_id: uuid.UUID, payload: ReclassifyPayload, db: AsyncSession = Depends(get_db)):
    event = await get_event_by_id(db, event_id)
    if not event: raise HTTPException(404, "Event not found")
    await update_event_classification(db, event_id, payload.new_classification, "RECLASSIFIED")
    return await save_feedback(db, event, payload.reviewer, payload.comment, payload.new_classification)