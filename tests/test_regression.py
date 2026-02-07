"""
Comprehensive regression tests for all API endpoints.
Tests backwards compatibility and ensures no existing functionality is broken.
"""
import pytest
import sys
sys.path.insert(0, r'c:\Users\KARTHIKEYAN D\Desktop\AI-SHIP-ROUTE-RECOVERY')

from backend.app.services.route_service import route_service
from backend.app.services.ship_service import ship_service
from backend.app.data.ports_database import port_db
from backend.app.utils.emissions import emissions_calc


class TestRouteServiceRegression:
    """Regression tests for route service."""
    
    def test_optimize_route_basic(self):
        """Test basic route optimization still works."""
        result = route_service.optimize_route(
            ship_id="TEST123",
            start_port="Singapore",
            end_port="Rotterdam"
        )
        assert result is not None
        assert result.ship_id == "TEST123"
        assert result.distance_km > 0
        assert result.estimated_time_hours > 0
        assert len(result.optimized_route) > 0
    
    def test_route_caching(self):
        """Test that route caching still works."""
        # First call
        result1 = route_service.optimize_route(
            "TEST", "Singapore", "Rotterdam"
        )
        # Second call - should hit cache
        result2 = route_service.optimize_route(
            "TEST", "Singapore", "Rotterdam"
        )
        assert result1.distance_km == result2.distance_km
    
    def test_compare_routes(self):
        """Test route comparison feature."""
        result = route_service.compare_routes(
            ship_id="TEST123",
            start_port="Singapore",
            end_port="Los Angeles"
        )
        assert "routes" in result
        assert len(result["routes"]) == 3
        assert result["routes"][0]["route_name"] == "fastest"
        assert result["routes"][1]["route_name"] == "balanced"
        assert result["routes"][2]["route_name"] == "greenest"


class TestPortDatabaseRegression:
    """Regression tests for port database."""
    
    def test_major_ports_exist(self):
        """Test that major ports are available."""
        major_ports = [
            "Singapore", "Rotterdam", "Shanghai", "Los Angeles",
            "Hong Kong", "Hamburg", "Dubai"
        ]
        all_ports = port_db.get_all_ports()
        for port in major_ports:
            assert port in all_ports, f"{port} missing from database"
    
    def test_port_search(self):
        """Test port search functionality."""
        results = port_db.search_ports("sing")
        assert "Singapore" in results
    
    def test_get_port_coords(self):
        """Test getting port coordinates."""
        coords = port_db.get_port_coords("Singapore")
        assert isinstance(coords, tuple)
        assert len(coords) == 2
        assert -90 <= coords[0] <= 90  # valid latitude
        assert -180 <= coords[1] <= 180  # valid longitude


class TestEmissionsCalculatorRegression:
    """Regression tests for emissions calculator."""
    
    def test_basic_emissions_calculation(self):
        """Test basic CO2 calculation."""
        result = emissions_calc.calculate_co2_emissions(
            distance_km=1000,
            speed_knots=12.0
        )
        assert "total_co2_tonnes" in result
        assert "fuel_consumed_tonnes" in result
        assert result["total_co2_tonnes"] > 0
    
    def test_different_vessel_types(self):
        """Test emissions for different vessel types."""
        container_result = emissions_calc.calculate_co2_emissions(
            distance_km=1000,
            speed_knots=12.0,
            vessel_type="container"
        )
        tanker_result = emissions_calc.calculate_co2_emissions(
            distance_km=1000,
            speed_knots=12.0,
            vessel_type="tanker"
        )
        assert container_result["total_co2_tonnes"] > 0
        assert tanker_result["total_co2_tonnes"] > 0


class TestBackwardCompatibility:
    """Tests to ensure backward compatibility with existing code."""
    
    def test_route_service_exists(self):
        """Test that route_service instance exists."""
        assert route_service is not None
    
    def test_ship_service_exists(self):
        """Test that ship_service instance exists."""
        assert ship_service is not None
    
    def test_get_all_ports_returns_list(self):
        """Test that get_all_ports returns a list."""
        ports = port_db.get_all_ports()
        assert isinstance(ports, list)
        assert len(ports) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
