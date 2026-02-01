"""Weather API tests."""
import pytest
from fastapi import status


def test_get_weather_no_auth(client):
    """Test weather endpoint without authentication (should work)."""
    response = client.get("/api/v1/weather?lat=0.0&lon=0.0")
    # May return 503 if API key not configured, or 200 if configured
    assert response.status_code in [200, 503]


def test_get_weather_with_auth(auth_headers, client):
    """Test weather endpoint with authentication."""
    response = client.get(
        "/api/v1/weather?lat=0.0&lon=0.0",
        headers=auth_headers
    )
    assert response.status_code in [200, 503]


def test_get_weather_validation(client):
    """Test weather endpoint input validation."""
    # Invalid latitude
    response = client.get("/api/v1/weather?lat=100&lon=0.0")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Invalid longitude
    response = client.get("/api/v1/weather?lat=0.0&lon=200")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
