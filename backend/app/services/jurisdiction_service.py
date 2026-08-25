from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.geography import AdminBoundary


async def resolve_jurisdiction(db: AsyncSession, latitude: float, longitude: float) -> tuple[Optional[str], Optional[str]]:
    point = func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326)
    result = await db.execute(
        select(AdminBoundary.state_name, AdminBoundary.district_name)
        .where(AdminBoundary.level == "DISTRICT")
        .where(func.ST_Contains(AdminBoundary.geometry, point))
        .limit(1)
    )
    row = result.one_or_none()
    return (row[0], row[1]) if row else (None, None)