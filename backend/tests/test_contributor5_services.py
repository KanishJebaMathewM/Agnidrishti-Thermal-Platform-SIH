import pytest

from app.services.jurisdiction_service import InvalidCoordinates, resolve_jurisdiction
from app.services.routing_service import resolve_alert_route


class Result:
    def __init__(self, row=None, rows=None):
        self.row = row
        self.rows = rows or []

    def fetchone(self):
        return self.row

    def fetchall(self):
        return self.rows


class Row:
    def __init__(self, **values):
        self._mapping = values
        for key, value in values.items():
            setattr(self, key, value)


class Session:
    def __init__(self, results):
        self.results = iter(results)
        self.calls = []

    async def execute(self, query, params):
        self.calls.append((str(query), params))
        return next(self.results)


@pytest.mark.asyncio
async def test_jurisdiction_resolves_postgis_row():
    db = Session([Result(Row(state_id="KL", state_name="Kerala", district_id="ERK", district_name="Ernakulam"))])
    result = await resolve_jurisdiction(db, 10.0, 76.0)
    assert result["district_name"] == "Ernakulam"
    assert db.calls[0][1] == {"lat": 10.0, "lon": 76.0}


@pytest.mark.asyncio
async def test_jurisdiction_returns_unknown_when_unmatched():
    result = await resolve_jurisdiction(Session([Result()]), 10, 76)
    assert result["state_id"] == "UNKNOWN"


@pytest.mark.asyncio
async def test_invalid_coordinates_are_rejected():
    with pytest.raises(InvalidCoordinates):
        await resolve_jurisdiction(Session([]), 100, 76)


@pytest.mark.asyncio
async def test_routing_orders_authorities_by_classification():
    db = Session([Result(Row(state_id="KL", state_name="Kerala", district_id="ERK", district_name="Ernakulam"))])

    async def lookup(_db, _state, _district, types):
        assert types[0] == "PLANT_EMERGENCY"
        return [{"id": "primary"}, {"id": "secondary"}]

    result = await resolve_alert_route(db, 10, 76, "Industrial Incident", "HIGH", lookup)
    assert result["primary_authority"]["id"] == "primary"
    assert result["secondary_authorities"][0]["id"] == "secondary"
