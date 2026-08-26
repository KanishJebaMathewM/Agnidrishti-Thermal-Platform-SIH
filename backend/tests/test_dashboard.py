from app.main import app


def test_dashboard_routes_are_registered():
    # app.routes' internal Route/_IncludedRouter representation is a FastAPI
    # implementation detail that changed shape across the version bump this
    # project needed for Python 3.14 support; app.openapi()["paths"] is the
    # stable public contract for "what paths does this app expose".
    paths = set(app.openapi()["paths"].keys())
    assert {"/dashboard/summary", "/dashboard/map", "/dashboard/trends"}.issubset(paths)
