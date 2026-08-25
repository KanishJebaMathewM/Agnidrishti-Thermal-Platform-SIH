from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, update, desc
from datetime import datetime, timedelta
import uuid
from typing import List, Optional, Tuple, Dict, Any

from app.models.event import Event, event_observations
from app.models.observation import Observation
from app.models.thermal_source import ThermalSource

async def get_events(
    db: AsyncSession,
    limit: int = 50,
    offset: int = 0,
    state: Optional[str] = None,
    classification: Optional[str] = None,
    status: Optional[str] = None,
    anomaly_only: bool = False,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
) -> Tuple[List[Event], int]:
    """Retrieve paginated events with optional filters."""
    query = select(Event)
    count_query = select(func.count()).select_from(Event)

    filters = []
    if state:
        filters.append(Event.state.ilike(f"%{state}%"))
    if classification:
        filters.append(Event.classification == classification)
    if status:
        # Convert frontend status back to internal status if needed
        status_map = {
            "Escalated": "CONFIRMED",
            "Suppressed": "FALSE_ALARM",
            "Under Review": "NEW"
        }
        internal_status = status_map.get(status, status)
        filters.append(Event.status == internal_status)
    if anomaly_only:
        filters.append(Event.anomaly_flag == True)
    if from_date:
        filters.append(Event.first_seen >= from_date)
    if to_date:
        filters.append(Event.last_seen <= to_date)

    if filters:
        query = query.where(and_(*filters))
        count_query = count_query.where(and_(*filters))

    # Order by most recent first
    query = query.order_by(desc(Event.first_seen)).limit(limit).offset(offset)

    result = await db.execute(query)
    count_result = await db.execute(count_query)

    return list(result.scalars().all()), count_result.scalar_one()

async def get_event_by_id(db: AsyncSession, event_id: uuid.UUID) -> Optional[Event]:
    """Retrieve a single event by ID."""
    query = select(Event).where(Event.id == event_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def update_event_status(db: AsyncSession, event_id: uuid.UUID, status: str) -> Optional[Event]:
    """Update event status."""
    stmt = (
        update(Event)
        .where(Event.id == event_id)
        .values(status=status, updated_at=datetime.utcnow())
        .returning(Event)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.scalar_one_or_none()

async def update_event_classification(
    db: AsyncSession, event_id: uuid.UUID, new_classification: str, status: str
) -> Optional[Event]:
    """Update event classification and status."""
    stmt = (
        update(Event)
        .where(Event.id == event_id)
        .values(classification=new_classification, status=status, updated_at=datetime.utcnow())
        .returning(Event)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.scalar_one_or_none()

async def get_recent_events(db: AsyncSession, limit: int = 5) -> List[Event]:
    """Get the N most recent events."""
    query = select(Event).order_by(desc(Event.first_seen)).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())

async def get_events_count_24h(db: AsyncSession) -> int:
    """Count events created in the last 24 hours."""
    since = datetime.utcnow() - timedelta(hours=24)
    query = select(func.count()).select_from(Event).where(Event.first_seen >= since)
    result = await db.execute(query)
    return result.scalar_one()

async def get_anomaly_events_count_24h(db: AsyncSession) -> int:
    """Count anomaly events in the last 24 hours."""
    since = datetime.utcnow() - timedelta(hours=24)
    query = select(func.count()).select_from(Event).where(
        and_(Event.first_seen >= since, Event.anomaly_flag == True)
    )
    result = await db.execute(query)
    return result.scalar_one()

async def get_critical_events_count(db: AsyncSession) -> int:
    """Count events flagged as CRITICAL or HIGH severity."""
    query = select(func.count()).select_from(Event).where(
        Event.severity.in_(["HIGH", "CRITICAL"])
    )
    result = await db.execute(query)
    return result.scalar_one()

async def get_classification_distribution(db: AsyncSession) -> List[Dict[str, Any]]:
    """Group events by classification."""
    query = select(Event.classification, func.count()).group_by(Event.classification)
    result = await db.execute(query)
    
    dist = []
    total = 0
    raw_data = result.all()
    for row in raw_data:
        total += row[1]
        
    colors = {
        "Industrial Incident": "#EF4444",
        "Persistent Flare/Kiln": "#F97316",
        "Agricultural Burn": "#22C55E",
        "Forest Fire": "#A855F7",
        "Unknown": "#64748B"
    }
    
    for row in raw_data:
        pct = (row[1] / total * 100) if total > 0 else 0
        dist.append({
            "name": row[0],
            "value": row[1],
            "pct": f"{pct:.1f}%",
            "color": colors.get(row[0], "#64748B")
        })
    return dist

async def get_risk_level_summary(db: AsyncSession) -> List[Dict[str, Any]]:
    """Group events by severity/risk level."""
    query = select(Event.severity, func.count()).group_by(Event.severity)
    result = await db.execute(query)
    
    counts = {row[0]: row[1] for row in result.all()}
    total = sum(counts.values())
    
    levels = [
        {"name": "High Risk", "db_keys": ["CRITICAL", "HIGH"], "color": "#EF4444"},
        {"name": "Medium Risk", "db_keys": ["REVIEW"], "color": "#F97316"},
        {"name": "Low Risk", "db_keys": ["OBSERVE"], "color": "#22C55E"},
        {"name": "Informational", "db_keys": ["NORMAL"], "color": "#0D9488"}
    ]
    
    summary = []
    for level in levels:
        count = sum(counts.get(k, 0) for k in level["db_keys"])
        pct = (count / total * 100) if total > 0 else 0
        summary.append({
            "name": level["name"],
            "count": count,
            "pct": f"{int(pct)}%",
            "color": level["color"]
        })
    return summary

async def get_state_anomaly_data(db: AsyncSession) -> List[Dict[str, Any]]:
    """Group anomalies and total events by state."""
    query = select(
        Event.state,
        func.count().filter(Event.anomaly_flag == True),
        func.count()
    ).group_by(Event.state).order_by(desc(func.count().filter(Event.anomaly_flag == True))).limit(10)
    
    result = await db.execute(query)
    return [
        {"state": row[0] or "Unknown", "anomalies": row[1], "total": row[2]}
        for row in result.all()
    ]

async def get_event_timeline(db: AsyncSession, event_id: uuid.UUID) -> List[Observation]:
    """Retrieve chronological observations associated with the event."""
    query = (
        select(Observation)
        .join(event_observations, Observation.id == event_observations.c.observation_id)
        .where(event_observations.c.event_id == event_id)
        .order_by(Observation.timestamp_utc)
    )
    result = await db.execute(query)
    return list(result.scalars().all())
