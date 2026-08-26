from app.main import app


def test_routing_endpoint_is_registered_before_authority_id_route():
    paths = [route.path for route in app.routes]
    assert "/authorities/routing/resolve" in paths
    assert paths.index("/authorities/routing/resolve") < paths.index("/authorities/{authority_id}")
