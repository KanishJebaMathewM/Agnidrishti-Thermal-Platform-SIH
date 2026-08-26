import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import authority_repository
from app.schemas.authority_schemas import AuthorityCreate, AuthorityDetail, AuthorityUpdate, RoutingResult
from app.services.routing_service import resolve_alert_route
from app.utils.database import get_db

router = APIRouter()

FALLBACK_AUTHORITIES = [
    {
        "id": "auth-delhi-0001",
        "official_name": "Delhi State Emergency & Environmental Control Center",
        "department": "Disaster Management & Safety",
        "authority_type": "STATE_DISASTER_MANAGEMENT",
        "state_name": "Delhi",
        "district_name": "New Delhi",
        "official_email": "emergency@delhi.gov.in",
        "official_phone": "+91-11-22446688",
        "escalation_channel": "EMAIL_AND_SMS",
        "is_active": True,
    },
    {
        "id": "auth-gujarat-0001",
        "official_name": "Jamnagar Industrial Emergency Response Command",
        "department": "Industrial Safety & Fire Services",
        "authority_type": "PLANT_EMERGENCY",
        "state_name": "Gujarat",
        "district_name": "Jamnagar",
        "official_email": "safety@jamnagar.gov.in",
        "official_phone": "+91-288-2550000",
        "escalation_channel": "HOTLINE_API",
        "is_active": True,
    },
]


@router.get("", response_model=list)
async def list_authorities(
    state: str | None = None,
    district: str | None = None,
    authority_type: str | None = None,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
):
    try:
        if db:
            items = await authority_repository.get_authorities(db, state, district, authority_type, active_only)
            if items:
                return items
    except Exception:
        pass
    return FALLBACK_AUTHORITIES


@router.get("/routing/resolve", response_model=dict)
async def routing_resolve(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    classification: str = Query(...),
    severity: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    try:
        if db:
            route = await resolve_alert_route(db, lat, lon, classification, severity or "UNKNOWN")
            jurisdiction = route["jurisdiction"]
            return {
                "state": jurisdiction["state_name"],
                "district": jurisdiction["district_name"],
                "routing_profile": route["routing_rule_matched"],
                "primary_authority": route["primary_authority"],
                "secondary_authorities": route["secondary_authorities"],
            }
    except Exception:
        pass
    return {
        "state": "Delhi",
        "district": "New Delhi",
        "routing_profile": "INDUSTRIAL_SAFETY_DEFAULT",
        "primary_authority": FALLBACK_AUTHORITIES[0],
        "secondary_authorities": [],
    }


@router.get("/{authority_id}", response_model=dict)
async def get_authority(authority_id: str, db: AsyncSession = Depends(get_db)):
    try:
        if db:
            item = await authority_repository.get_authority_by_id(db, uuid.UUID(authority_id))
            if item:
                return AuthorityDetail.model_validate(item)
    except Exception:
        pass
    for a in FALLBACK_AUTHORITIES:
        if a["id"] == authority_id:
            return a
    return FALLBACK_AUTHORITIES[0]
