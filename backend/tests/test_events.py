from app.main import app


def test_event_routes_are_registered():
    # See test_dashboard.py: app.openapi()["paths"] is the stable public
    # contract, not the version-fragile internal app.routes representation.
    paths = set(app.openapi()["paths"].keys())
    assert "/events" in paths
    assert "/events/{event_id}" in paths
    assert "/events/{event_id}/timeline" in paths
