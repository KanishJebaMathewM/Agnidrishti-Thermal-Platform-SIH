from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
import uuid
from typing import List, Optional, Tuple

from app.models.thermal_source import ThermalSource
from app.models.observation import Observation

async def get_sources(
    db: AsyncSession,
    limit: int = 50,
    offset: int = 0,
    state: Optional[str] = None,
    status: Optional[str] = None,
    expected_class: Optional[str] = None,
) -> Tuple[List[ThermalSource], int]:
    """Retrieve thermal sources with pagination and filtering."""
    query = select(ThermalSource)
    count_query = select(func.count()).select_from(ThermalSource)

    filters = []
    if state:
        filters.append(ThermalSource.state == state)
    if status:
        filters.append(ThermalSource.status == status)
    if expected_class:
        filters.append(ThermalSource.expected_class == expected_class)

    if filters:
        query = query.where(and_(*filters))
        count_query = count_query.where(and_(*filters))

    query = query.limit(limit).offset(offset)
    
    result = await db.execute(query)
    count_result = await db.execute(count_query)
    
    return list(result.scalars().all()), count_result.scalar_one()

async def get_source_by_id(db: AsyncSession, source_id: uuid.UUID) -> Optional[ThermalSource]:
    """Retrieve thermal source detail."""
    query = select(ThermalSource).where(ThermalSource.id == source_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_source_history(
    db: AsyncSession, source_id: uuid.UUID, limit: int = 50, offset: int = 0
) -> Tuple[List[Observation], int]:
    """Retrieve observation history for a specific thermal source."""
    query = select(Observation).where(Observation.source_id == source_id).order_by(desc(Observation.timestamp_utc))
    count_query = select(func.count()).select_from(Observation).where(Observation.source_id == source_id)

    query = query.limit(limit).offset(offset)
    
    result = await db.execute(query)
    count_result = await db.execute(count_query)
    
    return list(result.scalars().all()), count_result.scalar_one()

async def get_active_sources_count(db: AsyncSession) -> int:
    """Count registered active sources in the system."""
    query = select(func.count()).select_from(ThermalSource).where(ThermalSource.status == "MONITORED")
    result = await db.execute(query)
    return result.scalar_one()
