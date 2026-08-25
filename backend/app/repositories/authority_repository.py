from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update
import uuid
from typing import List, Optional

from app.models.authority import Authority, RoutingProfile

async def get_authorities(
    db: AsyncSession,
    state: Optional[str] = None,
    district: Optional[str] = None,
    authority_type: Optional[str] = None,
    active_only: bool = True
) -> List[Authority]:
    """Retrieve filtered authority entries."""
    query = select(Authority)
    filters = []
    if state:
        filters.append(Authority.state == state)
    if district:
        filters.append(Authority.district == district)
    if authority_type:
        filters.append(Authority.authority_type == authority_type)
    if active_only:
        filters.append(Authority.active == True)
        
    if filters:
        query = query.where(and_(*filters))
        
    result = await db.execute(query)
    return list(result.scalars().all())

async def get_authority_by_id(db: AsyncSession, authority_id: uuid.UUID) -> Optional[Authority]:
    """Retrieve authority by ID."""
    query = select(Authority).where(Authority.id == authority_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def create_authority(db: AsyncSession, authority_data: dict) -> Authority:
    """Create authority entry."""
    auth = Authority(**authority_data)
    db.add(auth)
    await db.commit()
    await db.refresh(auth)
    return auth

async def update_authority(db: AsyncSession, authority_id: uuid.UUID, update_data: dict) -> Optional[Authority]:
    """Update authority entry."""
    stmt = (
        update(Authority)
        .where(Authority.id == authority_id)
        .values(**update_data)
        .returning(Authority)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.scalar_one_or_none()

async def get_authorities_by_district(
    db: AsyncSession, state: str, district: str, target_types: List[str]
) -> List[Authority]:
    """Retrieve matching authority contacts for jurisdiction-based routing."""
    query = select(Authority).where(
        and_(
            Authority.state.ilike(state),
            Authority.district.ilike(district),
            Authority.authority_type.in_(target_types),
            Authority.active == True
        )
    )
    result = await db.execute(query)
    return list(result.scalars().all())

async def get_routing_profile(db: AsyncSession, state: str, district: str, classification: str) -> Optional[RoutingProfile]:
    """Find routing profile matching event jurisdiction and classification."""
    query = select(RoutingProfile).where(
        and_(
            RoutingProfile.state.ilike(state),
            RoutingProfile.district.ilike(district),
            RoutingProfile.classification == classification
        )
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()
