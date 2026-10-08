import asyncio

from app import health_check, readiness_check


def test_health_endpoint():
    response = asyncio.run(health_check())

    assert response["status"] == "ok"
    assert response["service"] == "crewai-content-engine"


def test_readiness_endpoint():
    response = asyncio.run(readiness_check())

    assert response["status"] == "ready"
    assert response["service"] == "crewai-content-engine"
