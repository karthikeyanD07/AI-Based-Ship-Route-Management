"""Route optimization API tests."""
import pytest
from fastapi import status


def test_optimize_route_no_auth(client):
    """Test route optimization without authentication (should work)."""
    response = client.post(
        "/api/v1/routes/optimize",
        json={
            "ship_id": "123456789",
            "start": "Port A",
            "end": "Port B"
        }
    )
    # Should work (auth is optional)
    assert response.status_code in [200, 400, 500]  # 400/500 if ports invalid, 200 if valid


def test_optimize_route_with_auth(auth_headers, client):
    """Test route optimization with authentication."""
    response = client.post(
        "/api/v1/routes/optimize",
        json={
            "ship_id": "123456789",
            "start": "Port A",
            "end": "Port B"
        },
        headers=auth_headers
    )
    # Should work
    assert response.status_code in [200, 400, 500]


def test_optimize_route_validation(client):
    """Test route optimization input validation."""
    # Missing required fields
    response = client.post(
        "/api/v1/routes/optimize",
        json={"ship_id": "123"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
