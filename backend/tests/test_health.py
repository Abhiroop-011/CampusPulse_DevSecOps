"""
Tests for the /health and /ready probe endpoints.
"""


def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_ready_endpoint_exists(client):
    """
    /ready may return 200 (connected) or 503 depending on DB availability.
    In tests the DB is SQLite so check_db_connection may return False —
    we only assert the endpoint responds with a known status key.
    """
    response = client.get("/ready")
    data = response.json()
    assert "status" in data
    assert "database" in data


def test_root_returns_api_info(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "CampusPulse API"
    assert "health" in data
    assert "docs" in data
