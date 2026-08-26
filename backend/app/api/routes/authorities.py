import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import authority_repository
from app.schemas.authority_schemas import AuthorityCreate, AuthorityDetail, AuthorityUpdate, RoutingResult
from app.services.routing_service import resolve_alert_route
from app.utils.database import get_db

router = APIRouter()


@router.get("", response_model=list[AuthorityDetail])
async def list_authorities(state: str | None = None, district: str | None = None, authority_type: str | None = None,
                           active_only: bool = True, db: AsyncSession = Depends(get_db)):
    return await authority_repository.get_authorities(db, state, district, authority_type, active_only)


@router.get("/routing/resolve", response_model=RoutingResult)
async def routing_resolve(lat: float = Query(..., ge=-90, le=90), lon: float = Query(..., ge=-180, le=180),
                          classification: str = Query(...), severity: str | None = None, db: AsyncSession = Depends(get_db)):
    route = await resolve_alert_route(db, lat, lon, classification, severity or "UNKNOWN")
    jurisdiction = route["jurisdiction"]
    return RoutingResult(
        state=jurisdiction["state_name"],
        district=jurisdiction["district_name"],
        routing_profile=route["routing_rule_matched"],
        primary_authority=route["primary_authority"],
        secondary_authorities=route["secondary_authorities"],
    )


@router.get("/{authority_id}", response_model=AuthorityDetail)
async def get_authority(authority_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    authority = await authority_repository.get_authority_by_id(db, authority_id)
    if not authority:
        raise HTTPException(404, "Authority not found")
    return authority


@router.post("", response_model=AuthorityDetail, status_code=201)
async def create_authority(payload: AuthorityCreate, db: AsyncSession = Depends(get_db)):
    return await authority_repository.create_authority(db, payload.model_dump())


@router.patch("/{authority_id}", response_model=AuthorityDetail)
async def update_authority(authority_id: uuid.UUID, payload: AuthorityUpdate, db: AsyncSession = Depends(get_db)):
    authority = await authority_repository.update_authority(db, authority_id, payload.model_dump(exclude_unset=True))
    if not authority:
        raise HTTPException(404, "Authority not found")
    return authority

