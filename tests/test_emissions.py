"""Unit tests for emissions calculator."""
import pytest
from backend.app.utils.emissions import emissions_calc


def test_fuel_consumption_calculation():
    """Test basic fuel consumption calculation."""
    result = emissions_calc.calculate_fuel_consumption(
        distance_km=1000,
        speed_knots=12.0,
        vessel_type="container",
        vessel_size="medium"
    )
    
    assert "fuel_tonnes" in result
    assert "voyage_hours" in result
    assert result["fuel_tonnes"] > 0
    assert result["voyage_hours"] > 0


def test_co2_emissions_calculation():
    """Test CO2 emissions calculation."""
    result = emissions_calc.calculate_co2_emissions(
        distance_km=1000,
        speed_knots=12.0,
        vessel_type="container",
        vessel_size="medium",
        fuel_type="HFO"
    )
    
    assert "total_co2_tonnes" in result
    assert "fuel_consumed_tonnes" in result
    assert result["total_co2_tonnes"] > 0


def test_emissions_by_vessel_type():
    """Test that different vessel types have different consumption."""
    container_result = emissions_calc.calculate_co2_emissions(
        distance_km=1000, speed_knots=12.0, 
        vessel_type="container", vessel_size="large"
    )
    
    general_cargo_result = emissions_calc.calculate_co2_emissions(
        distance_km=1000, speed_knots=12.0,
        vessel_type="general_cargo", vessel_size="medium"
    )
    
    # Container ships consume more fuel than general cargo
    assert container_result["fuel_consumed_tonnes"] > general_cargo_result["fuel_consumed_tonnes"]


def test_route_comparison():
    """Test route comparison functionality."""
    routes = [
        {"name": "Route A", "distance_km": 1000},
        {"name": "Route B", "distance_km": 1200},
    ]
    
    results = emissions_calc.compare_routes(routes, speed_knots=12.0)
    
    assert len(results) == 2
    assert results[0]["total_co2_tonnes"] < results[1]["total_co2_tonnes"]
