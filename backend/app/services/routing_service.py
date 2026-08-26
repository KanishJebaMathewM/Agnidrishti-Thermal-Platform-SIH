from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.authority_repository import get_routing_profile, get_authority_by_id
from app.schemas.authority_schemas import RoutingResult


async def resolve_route(db: AsyncSession, state: str, district: str, classification: str) -> RoutingResult:
    profile = await get_routing_profile(db, state, district, classification)
    if not profile:
        return RoutingResult(state=state, district=district)
    primary = await get_authority_by_id(db, profile.primary_authority_id)
    secondary = []
    for authority_id in profile.secondary_authority_ids or []:
        authority = await get_authority_by_id(db, authority_id)
        if authority:
            secondary.append(authority)
    return RoutingResult(
        state=state,
        district=district,
        routing_profile=profile.name,
        primary_authority=primary,
        secondary_authorities=secondary,
    )