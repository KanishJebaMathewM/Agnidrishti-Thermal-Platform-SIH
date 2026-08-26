"""Deterministic event-to-authority routing."""

from __future__ import annotations

from typing import Any, Awaitable, Callable

from app.services.jurisdiction_service import resolve_jurisdiction

CLASSIFICATION_AUTHORITY_TYPES: dict[str, tuple[str, ...]] = {
    "Industrial Incident": ("PLANT_EMERGENCY", "FIRE_RESPONSE", "DISTRICT_EMERGENCY"),
    "Forest Fire": ("FOREST_RESPONSE", "FIRE_RESPONSE", "DISTRICT_EMERGENCY"),
    "Agricultural Burn": ("POLLUTION_CONTROL", "DISTRICT_EMERGENCY"),
    "Persistent Flare/Kiln": ("POLLUTION_CONTROL", "PLANT_EMERGENCY"),
    "Unknown": ("DISTRICT_EMERGENCY",),
}


async def _query_authorities(db: Any, state: str, district: str, types: tuple[str, ...]) -> list[dict[str, Any]]:
    from sqlalchemy import text

    result = await db.execute(
        text(
            """
            SELECT id, state, district, authority_type, department, role,
                   official_email, official_phone, portal_url, active,
                   verified_on, source_url, created_at, updated_at
            FROM authorities
            WHERE state = :state AND district = :district
              AND authority_type = ANY(:authority_types)
              AND active = TRUE
            ORDER BY array_position(:authority_types, authority_type), department, role
            """
        ),
        {"state": state, "district": district, "authority_types": list(types)},
    )
    return [dict(row._mapping) for row in result.fetchall()]


async def resolve_alert_route(
    db: Any,
    lat: float,
    lon: float,
    classification: str,
    severity: str,
    authority_lookup: Callable[[Any, str, str, tuple[str, ...]], Awaitable[list[dict[str, Any]]]] | None = None,
) -> dict[str, Any]:
    """Resolve jurisdiction and configured contacts without discovering contacts."""
    jurisdiction = await resolve_jurisdiction(db, lat, lon)
    target_types = CLASSIFICATION_AUTHORITY_TYPES.get(classification, CLASSIFICATION_AUTHORITY_TYPES["Unknown"])
    lookup = authority_lookup or _query_authorities
    authorities = await lookup(
        db,
        jurisdiction["state_name"],
        jurisdiction["district_name"],
        target_types,
    )
    return {
        "jurisdiction": jurisdiction,
        "classification": classification,
        "severity": severity,
        "primary_authority": authorities[0] if authorities else None,
        "secondary_authorities": authorities[1:],
        "routing_rule_matched": f"{classification.lower().replace(' ', '_')}_{jurisdiction['state_name'].lower().replace(' ', '_')}_rule",
        "authority_types_considered": list(target_types),
    }
