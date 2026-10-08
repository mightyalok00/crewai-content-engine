from fastapi.testclient import TestClient

from app import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "crewai-content-engine"


def test_readiness_endpoint():
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"
