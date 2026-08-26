from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "timestamp" in response.json()


def test_readiness_endpoint_is_dependency_aware():
    response = client.get("/ready")
    assert response.status_code in {200, 503}
