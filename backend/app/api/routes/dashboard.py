from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import event_repository, source_repository
from app.schemas.dashboard_schemas import DashboardSummary, MapEventsResponse, TrendsResponse
from app.schemas.event_schemas import EventSummary
from app.utils.database import get_db

router = APIRouter()


@router.get("/summary", response_model=DashboardSummary)
async def summary(db: AsyncSession = Depends(get_db)):
    total = await event_repository.get_events_count_24h(db)
    anomaly = await event_repository.get_anomaly_events_count_24h(db)
    events = await event_repository.get_recent_events(db)
    return {"total_events_24h": total, "anomaly_events_24h": anomaly,
            "critical_events": await event_repository.get_critical_events_count(db),
            "active_sources": await source_repository.get_active_sources_count(db),
            "classification_distribution": await event_repository.get_classification_distribution(db),
            "risk_level_summary": await event_repository.get_risk_level_summary(db),
            "state_anomaly_data": await event_repository.get_state_anomaly_data(db),
            "recent_events": [EventSummary.model_validate(event) for event in events]}


@router.get("/map", response_model=MapEventsResponse)
async def map_events(db: AsyncSession = Depends(get_db)):
    events, _ = await event_repository.get_events(db, limit=10000)
    return {"events": [{"id": str(event.id), "lat": event.centroid_lat, "lon": event.centroid_lon,
                         "classification": event.classification, "severity": event.severity,
                         "confidence": (event.classification_confidence or 0) * 100 if (event.classification_confidence or 0) <= 1 else (event.classification_confidence or 0),
                         "anomaly_flag": event.anomaly_flag} for event in events]}


@router.get("/trends", response_model=TrendsResponse)
async def trends(db: AsyncSession = Depends(get_db)):
    return {"points": []}