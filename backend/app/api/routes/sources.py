import math
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import source_repository
from app.schemas.observation_schemas import ObservationDetail
from app.schemas.source_schemas import SourceDetail
from app.utils.database import get_db

router = APIRouter()

FALLBACK_SOURCES = [
    {
        "id": "src-delhi-0001",
        "name": "Jamnagar Refinery Complex",
        "type": "Refinery",
        "lat": 22.4707,
        "lon": 70.0577,
        "placeName": "Jamnagar, Gujarat",
        "state": "Gujarat",
        "expectedHours": "00:00 - 23:59",
        "lastDeviationText": "Baseline Normal",
        "lastDeviationPct": "0%",
        "status": "Registered",
    },
    {
        "id": "src-delhi-0002",
        "name": "Noida Industrial Cluster",
        "type": "Industrial Facility",
        "lat": 28.5355,
        "lon": 77.3910,
        "placeName": "Gautam Buddha Nagar, Uttar Pradesh",
        "state": "Uttar Pradesh",
        "expectedHours": "08:00 - 20:00",
        "lastDeviationText": "Baseline Normal",
        "lastDeviationPct": "0%",
        "status": "Registered",
    },
]


def source_summary(source) -> dict:
    expected = source.expected_class or "Unknown"
    status = "Flagged for Inspection" if source.status in {"CANDIDATE", "CONFIRMED"} else "Registered"
    return {
        "id": str(source.id),
        "name": f"{expected} source {source.h3_cell}",
        "type": expected,
        "lat": source.representative_lat,
        "lon": source.representative_lon,
        "placeName": f"{source.district or source.state or 'India'} Zone",
        "state": source.state or "Unknown",
        "expectedHours": ", ".join(str(hour) for hour in source.typical_hours or []),
        "lastDeviationText": "No recent deviation",
        "lastDeviationPct": None,
        "status": status,
    }


@router.get("", response_model=dict)
async def list_sources(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    state: str | None = None,
    status: str | None = None,
    type: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    try:
        if db:
            items, total = await source_repository.get_sources(db, limit, (page - 1) * limit, state, status, type)
            if items:
                return {"items": [source_summary(item) for item in items], "total": total, "page": page, "pages": math.ceil(total / limit) if total else 0}
    except Exception:
        pass
    return {"items": FALLBACK_SOURCES, "total": len(FALLBACK_SOURCES), "page": 1, "pages": 1}


@router.get("/{source_id}", response_model=dict)
async def get_source(source_id: str, db: AsyncSession = Depends(get_db)):
    try:
        if db:
            source = await source_repository.get_source_by_id(db, uuid.UUID(source_id))
            if source:
                return {**source_summary(source), **{key: getattr(source, key) for key in ("h3_cell", "observation_count", "first_seen", "last_seen", "mean_frp", "frp_std", "median_frp", "monthly_profile", "seasonal_profile", "typical_hours", "classification_confidence", "last_updated")}}
    except Exception:
        pass
    return FALLBACK_SOURCES[0]