from app.main import app


def test_event_routes_are_registered():
    paths = {route.path for route in app.routes}
    assert "/events" in paths
    assert "/events/{event_id}" in paths
    assert "/events/{event_id}/timeline" in paths
