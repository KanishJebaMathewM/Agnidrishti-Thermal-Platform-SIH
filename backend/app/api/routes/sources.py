import math
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import source_repository
from app.schemas.observation_schemas import ObservationDetail
from app.schemas.source_schemas import SourceDetail, SourceSummary
from app.utils.database import get_db

router = APIRouter()


def source_summary(source) -> dict:
    expected = source.expected_class or "Unknown"
    status = "Flagged for Inspection" if source.status in {"CANDIDATE", "CONFIRMED"} else "Registered"
    return {"id": str(source.id), "name": f"{expected} source {source.h3_cell}", "type": expected,
            "lat": source.representative_lat, "lon": source.representative_lon,
            "placeName": f"{source.district or source.state or 'India'} Zone", "state": source.state or "Unknown",
            "expectedHours": ", ".join(str(hour) for hour in source.typical_hours or []),
            "lastDeviationText": "No recent deviation", "lastDeviationPct": None, "status": status}


@router.get("", response_model=dict)
async def list_sources(page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=200), state: str | None = None,
                       status: str | None = None, type: str | None = None, db: AsyncSession = Depends(get_db)):
    items, total = await source_repository.get_sources(db, limit, (page - 1) * limit, state, status, type)
    return {"items": [source_summary(item) for item in items], "total": total, "page": page, "pages": math.ceil(total / limit) if total else 0}


@router.get("/{source_id}", response_model=SourceDetail)
async def get_source(source_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    source = await source_repository.get_source_by_id(db, source_id)
    if not source:
        raise HTTPException(404, "Source not found")
    return {**source_summary(source), **{key: getattr(source, key) for key in ("h3_cell", "observation_count", "first_seen", "last_seen", "mean_frp", "frp_std", "median_frp", "monthly_profile", "seasonal_profile", "typical_hours", "classification_confidence", "last_updated")}}


@router.get("/{source_id}/history", response_model=dict)
async def source_history(source_id: uuid.UUID, page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=200), db: AsyncSession = Depends(get_db)):
    if not await source_repository.get_source_by_id(db, source_id):
        raise HTTPException(404, "Source not found")
    items, total = await source_repository.get_source_history(db, source_id, limit, (page - 1) * limit)
    return {"items": [ObservationDetail.model_validate(item) for item in items], "total": total, "page": page, "pages": math.ceil(total / limit) if total else 0}


@router.get("/{source_id}/baseline")
async def source_baseline(source_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    source = await source_repository.get_source_by_id(db, source_id)
    if not source:
        raise HTTPException(404, "Source not found")
    return {"mean_frp": source.mean_frp, "frp_std": source.frp_std, "median_frp": source.median_frp, "monthly_profile": source.monthly_profile, "seasonal_profile": source.seasonal_profile}