"""Health check tests."""
import pytest
from fastapi import status


def test_health_check(client):
    """Test basic health check."""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "healthy"


def test_detailed_health_check(client):
    """Test detailed health check."""
    response = client.get("/health/detailed")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "status" in data
    assert "dependencies" in data
    assert "database" in data["dependencies"]
