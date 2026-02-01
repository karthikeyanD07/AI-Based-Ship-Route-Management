"""Ship tracking API tests."""
import pytest
from fastapi import status


def test_get_ship_traffic_no_auth(client):
    """Test getting ship traffic without authentication (should work)."""
    response = client.get("/api/v1/ships")
    assert response.status_code == status.HTTP_200_OK
    assert "ships" in response.json()


def test_get_ship_traffic_with_auth(auth_headers, client):
    """Test getting ship traffic with authentication."""
    response = client.get("/api/v1/ships", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert "ships" in response.json()


def test_get_ship_traffic_pagination(client):
    """Test ship traffic pagination."""
    response = client.get("/api/v1/ships?limit=10&offset=0")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "ships" in data
    assert "total" in data
    assert "has_more" in data


def test_get_ship_by_mmsi(client):
    """Test getting specific ship by MMSI."""
    # First get all ships to find a valid MMSI
    response = client.get("/api/v1/ships?limit=1")
    if response.status_code == 200 and response.json().get("ships"):
        mmsi = response.json()["ships"][0]["MMSI"]
        response = client.get(f"/api/v1/ships/{mmsi}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["MMSI"] == mmsi


def test_get_ship_by_mmsi_not_found(client):
    """Test getting non-existent ship."""
    response = client.get("/api/v1/ships/999999999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
