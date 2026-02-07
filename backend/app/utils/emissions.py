"""
Emissions calculator for maritime route optimization.
Implements IMO (International Maritime Organization) CO2 calculation formulas.
"""
from typing import Dict, Optional
import math


class EmissionsCalculator:
    """
    Calculate CO2 emissions for ship voyages based on IMO guidelines.
    Uses Fourth IMO GHG Study 2020 emission factors.
    """
    
    # Emission factors in grams CO2 per gram of fuel (Fourth IMO GHG Study 2020)
    EMISSION_FACTORS = {
        "HFO": 3.114,  # Heavy Fuel Oil
        "MDO": 3.206,  # Marine Diesel Oil  
        "MGO": 3.206,  # Marine Gas Oil
        "LNG": 2.750,  # Liquefied Natural Gas
    }
    
    # Fuel consumption rates by vessel type (tonnes/day at typical service speed)
    # These are approximate values for planning purposes
    FUEL_CONSUMPTION_RATES = {
        "container": {
            "small": 30,     # <3000 TEU
            "medium": 80,    # 3000-8000 TEU
            "large": 150,    # 8000-14000 TEU
            "ultra": 200,    # >14000 TEU
        },
        "bulk": {
            "handysize": 25,
            "panamax": 35,
            "capesize": 45,
        },
        "tanker": {
            "product": 30,
            "aframax": 40,
            "suezmax": 50,
            "vlcc": 80,
        },
        "general_cargo": 20,
        "ro_ro": 40,
        "cruise": 150,
        "ferry": 50,
    }
    
    def __init__(self):
        pass
    
    def calculate_fuel_consumption(
        self,
        distance_km: float,
        speed_knots: float,
        vessel_type: str = "container",
        vessel_size: str = "medium",
        fuel_type: str = "HFO"
    ) -> Dict[str, float]:
        """
        Calculate fuel consumption for a voyage.
        
        Args:
            distance_km: Distance in kilometers
            speed_knots: Vessel speed in knots
            vessel_type: Type of vessel (container, bulk, tanker, etc.)
            vessel_size: Size classification (small, medium, large, etc.)
            fuel_type: Type of fuel used (HFO, MDO, MGO, LNG)
            
        Returns:
            Dict with fuel_tonnes and voyage_hours
        """
        # Convert distance to nautical miles
        distance_nm = distance_km / 1.852
        
        # Calculate voyage duration in hours
        voyage_hours = distance_nm / speed_knots
        voyage_days = voyage_hours / 24
        
        # Get base fuel consumption rate
        if vessel_type in self.FUEL_CONSUMPTION_RATES:
            if isinstance(self.FUEL_CONSUMPTION_RATES[vessel_type], dict):
                fuel_rate_per_day = self.FUEL_CONSUMPTION_RATES[vessel_type].get(
                    vessel_size, 
                    list(self.FUEL_CONSUMPTION_RATES[vessel_type].values())[0]
                )
            else:
                fuel_rate_per_day = self.FUEL_CONSUMPTION_RATES[vessel_type]
        else:
            # Default to medium container ship
            fuel_rate_per_day = 80
        
        # Calculate total fuel consumption
        fuel_tonnes = fuel_rate_per_day * voyage_days
        
        return {
            "fuel_tonnes": round(fuel_tonnes, 2),
            "voyage_hours": round(voyage_hours, 2),
            "voyage_days": round(voyage_days, 2),
            "fuel_rate_tonnes_per_day": fuel_rate_per_day
        }
    
    def calculate_co2_emissions(
        self,
        distance_km: float,
        speed_knots: float,
        vessel_type: str = "container",
        vessel_size: str = "medium",
        fuel_type: str = "HFO"
    ) -> Dict[str, any]:
        """
        Calculate CO2 emissions for a voyage using IMO methodology.
        
        Args:
            distance_km: Distance in kilometers
            speed_knots: Vessel speed in knots
            vessel_type: Type of vessel
            vessel_size: Size classification
            fuel_type: Type of fuel (HFO, MDO, MGO, LNG)
            
        Returns:
            Dict with emissions data and voyage details
        """
        # Get fuel consumption
        fuel_data = self.calculate_fuel_consumption(
            distance_km, speed_knots, vessel_type, vessel_size, fuel_type
        )
        
        # Get emission factor
        emission_factor = self.EMISSION_FACTORS.get(fuel_type, 3.114)
        
        # Calculate CO2 emissions (tonnes)
        # Formula: CO2 = Fuel Consumed (tonnes) × Emission Factor (tCO2/tFuel)
        fuel_tonnes = fuel_data["fuel_tonnes"]
        co2_tonnes = fuel_tonnes * emission_factor
        
        # Calculate emissions per distance
        co2_per_km = co2_tonnes / distance_km
        co2_per_nm = co2_tonnes / (distance_km / 1.852)
        
        return {
            "total_co2_tonnes": round(co2_tonnes, 2),
            "co2_per_km": round(co2_per_km, 4),
            "co2_per_nm": round(co2_per_nm, 4),
            "fuel_consumed_tonnes": fuel_data["fuel_tonnes"],
            "fuel_type": fuel_type,
            "emission_factor": emission_factor,
            "voyage_hours": fuel_data["voyage_hours"],
            "voyage_days": fuel_data["voyage_days"],
            "vessel_type": vessel_type,
            "vessel_size": vessel_size
        }
    
    def calculate_cii_rating(
        self,
        co2_tonnes: float,
        distance_nm: float,
        dwt: float,
        vessel_type: str = "bulk_carrier"
    ) -> Dict[str, any]:
        """
        Calculate Carbon Intensity Indicator (CII) rating per IMO regulations.
        CII measures grams of CO2 per tonne-mile.
        
        Args:
            co2_tonnes: Total CO2 emitted in tonnes
            distance_nm: Distance traveled in nautical miles
            dwt: Deadweight tonnage of vessel
            vessel_type: Type of vessel for reference line
            
        Returns:
            Dict with CII value and rating (A, B, C, D, E)
        """
        # Calculate CII (gCO2/tonne-mile)
        transport_work = dwt * distance_nm  # tonne-miles
        co2_grams = co2_tonnes * 1_000_000  # convert to grams
        
        if transport_work == 0:
            return None
        
        cii = co2_grams / transport_work
        
        # Reference CII values (these are simplified; actual IMO values vary by ship size)
        # Lower CII = better efficiency
        reference_cii = 10.0  # g CO2/tonne-mile (simplified)
        
        # Calculate rating boundaries (simplified)
        # A: <0.87 of reference
        # B: 0.87-0.94
        # C: 0.94-1.06
        # D: 1.06-1.18
        # E: >1.18
        
        ratio = cii / reference_cii
        
        if ratio < 0.87:
            rating = "A"  # Superior
        elif ratio < 0.94:
            rating = "B"  # Good
        elif ratio < 1.06:
            rating = "C"  # Moderate
        elif ratio < 1.18:
            rating = "D"  # Poor
        else:
            rating = "E"  # Inferior
        
        return {
            "cii_value": round(cii, 2),
            "cii_rating": rating,
            "ratio_to_reference": round(ratio, 3),
            "transport_work_tonne_miles": round(transport_work, 0)
        }
    
    def compare_routes(
        self,
        routes: list,
        speed_knots: float,
        vessel_type: str = "container",
        vessel_size: str = "medium",
        fuel_type: str = "HFO"
    ) -> list:
        """
        Compare emissions for multiple route options.
        
        Args:
            routes: List of route dicts with 'name' and 'distance_km'
            speed_knots: Vessel speed
            vessel_type: Type of vessel
            vessel_size: Size classification
            fuel_type: Fuel type
            
        Returns:
            List of routes with emissions data, sorted by CO2
        """
        results = []
        
        for route in routes:
            emissions = self.calculate_co2_emissions(
                route['distance_km'],
                speed_knots,
                vessel_type,
                vessel_size,
                fuel_type
            )
            
            results.append({
                "route_name": route.get('name', 'Unknown'),
                "distance_km": route['distance_km'],
                **emissions
            })
        
        # Sort by total CO2 (lowest first)
        results.sort(key=lambda x: x['total_co2_tonnes'])
        
        return results


# Global instance
emissions_calc = EmissionsCalculator()
