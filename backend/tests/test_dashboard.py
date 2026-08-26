from app.main import app


def test_dashboard_routes_are_registered():
    paths = {route.path for route in app.routes}
    assert {"/dashboard/summary", "/dashboard/map", "/dashboard/trends"}.issubset(paths)
