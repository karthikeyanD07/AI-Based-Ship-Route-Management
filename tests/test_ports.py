"""Unit tests for port database."""
import pytest
from backend.app.data.ports_database import port_db


def test_get_port_coordinates():
    """Test getting port coordinates."""
    coords = port_db.get_port_coords("Singapore")
    assert len(coords) == 2
    assert coords[0] == 1.2644  # lat
    assert coords[1] == 103.8223  # lon


def test_get_unknown_port():
    """Test that unknown port raises ValueError."""
    with pytest.raises(ValueError):
        port_db.get_port_coords("NonExistent")


def test_search_ports():
    """Test port search functionality."""
    results = port_db.search_ports("rotterdam")
    assert "Rotterdam" in results


def test_get_all_ports():
    """Test getting all ports."""
    ports = port_db.get_all_ports()
    assert len(ports) > 90  # Should have 100+ ports
    assert "Singapore" in ports
    assert "Rotterdam" in ports


def test_get_ports_by_country():
    """Test getting ports by country."""
    us_ports = port_db.get_ports_by_country("USA")
    assert len(us_ports) > 0
    assert "Los Angeles" in us_ports
    assert "New York" in us_ports


def test_nearest_port():
    """Test finding nearest ports."""
    nearest = port_db.get_nearest_port(lat=1.3, lon=104.0, limit=3)
    assert len(nearest) <= 3
    assert "distance_km" in nearest[0]
    # Singapore should be closest to these coordinates
    assert nearest[0]["name"] == "Singapore"
