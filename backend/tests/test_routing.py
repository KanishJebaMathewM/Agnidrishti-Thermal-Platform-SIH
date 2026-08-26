from app.main import app


def test_routing_endpoint_is_registered_before_authority_id_route():
    # See test_dashboard.py: app.openapi()["paths"] is the stable public
    # contract, not the version-fragile internal app.routes representation.
    # dict preserves insertion order, which mirrors route registration order.
    paths = list(app.openapi()["paths"].keys())
    assert "/authorities/routing/resolve" in paths
    assert paths.index("/authorities/routing/resolve") < paths.index("/authorities/{authority_id}")
