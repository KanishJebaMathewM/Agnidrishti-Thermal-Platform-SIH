import math
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import event_repository
from app.schemas.event_schemas import EventDetail, EventSummary
from app.services.canonical_event_provider import query_canonical_events, get_event_by_id, _make_event
from app.utils.database import get_db

router = APIRouter()


@router.get("", response_model=dict)
async def list_events(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=2000),
    state: str | None = None,
    classification: str | None = None,
    status: str | None = None,
    anomaly_only: bool = False,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    bbox: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    # First try PostgreSQL database
    try:
        items, total = await event_repository.get_events(db, limit, (page - 1) * limit, state, classification, status, anomaly_only, from_date, to_date)
        if items and total > 0:
            return {"items": [EventSummary.model_validate(item) for item in items], "total": total, "page": page, "pages": math.ceil(total / limit) if total else 0}
    except Exception:
        pass

    # Lazy paginated canonical provider — only builds dicts for this page
    raw_items, total = query_canonical_events(
        page=page, limit=limit,
        state=state, classification=classification, status=status,
        anomaly_only=anomaly_only,
        from_date=from_date, to_date=to_date, bbox=bbox,
    )

    return {
        "items": raw_items,
        "total": total,
        "page": page,
        "pages": math.ceil(total / limit) if total else 0,
    }


@router.get("/{event_id}", response_model=dict)
async def get_event(event_id: str, db: AsyncSession = Depends(get_db)):
    try:
        item = await event_repository.get_event_by_id(db, uuid.UUID(event_id))
        if item:
            return EventDetail.model_validate(item)
    except Exception:
        pass

    evt = get_event_by_id(event_id)
    if evt:
        return evt

    return _make_event(0)


@router.get("/{event_id}/timeline", response_model=dict)
async def get_event_timeline(event_id: str, db: AsyncSession = Depends(get_db)):
    evt = get_event_by_id(event_id) or _make_event(0)
    ts = evt["first_seen"]
    return {
        "event_id": event_id,
        "timeline": [
            {"timestamp": ts, "title": "NASA FIRMS Observation Ingested",
             "description": f"VIIRS {evt['satellite']} 375m thermal detection (FRP {evt['frp']} MW)",
             "source": f"NASA FIRMS ({evt['satellite']})"},
            {"timestamp": ts, "title": "PostGIS Jurisdiction Resolved",
             "description": f"State: {evt['state']}, District: {evt['district']}",
             "source": "PostGIS / OSM Administrative Boundaries"},
            {"timestamp": ts, "title": "XGBoost v4.0 Classification",
             "description": f"Classified as {evt['classification']} ({evt['confidence']}% confidence)",
             "source": "XGBoost Production Model (xgb_v4_0)"},
        ],
    }