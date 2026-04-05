# NeoECDIS Backend - STANDALONE VERSION
# Everything inline, no complex imports

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Tuple, Optional
import math
import traceback
import random
import time
import httpx
import json
import os
from datetime import datetime, timedelta

app = FastAPI(title="NeoECDIS API", version="2.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== PORT DATABASE ==========
PORTS = {
    "Singapore": {"lat": 1.2644, "lon": 103.8223},
    "Rotterdam": {"lat": 51.9225, "lon": 4.4792},
    "Shanghai": {"lat": 31.2304, "lon": 121.4737},
    "Hong Kong": {"lat": 22.3193, "lon": 114.1694},
    "Dubai": {"lat": 25.2764, "lon": 55.2962},
    "Los Angeles": {"lat": 33.7405, "lon": -118.2519},
    "Hamburg": {"lat": 53.5511, "lon": 9.9937},
    "Antwerp": {"lat": 51.2194, "lon": 4.4025},
    "New York": {"lat": 40.6728, "lon": -74.1536},
    "Tokyo": {"lat": 35.6528, "lon": 139.8395},
    "Busan": {"lat": 35.1796, "lon": 129.0756},
    "Mumbai":  {"lat": 18.9375, "lon": 72.8347},
    "Sydney": {"lat": -33.8688, "lon": 151.2093},
    "Santos": {"lat": -23.9539, "lon": -46.3333},
    "Barcelona": {"lat": 41.3851, "lon": 2.1734},
    "Vancouver": {"lat": 49.2827, "lon": -123.1207},
    "Houston": {"lat": 29.7305, "lon": -95.0892},
    "Miami": {"lat": 25.7785, "lon": -80.1826},
    "Chennai": {"lat": 13.0827, "lon": 80.2707},
    "Colombo": {"lat": 6.9271, "lon": 79.8612},
    "Manila": {"lat": 14.5995, "lon": 120.9842},
    "Jakarta": {"lat": -6.2088, "lon": 106.8456},
    "Bangkok": {"lat": 13.7563, "lon": 100.5018},
    "Istanbul": {"lat": 41.0082, "lon": 28.9784},
    "Alexandria": {"lat": 31.2001, "lon": 29.9187},
    "Durban": {"lat": -29.8587, "lon": 31.0218},
    "Le Havre": {"lat": 49.4944, "lon": 0.1079},
    "Felixstowe": {"lat": 51.9500, "lon": 1.3500},
    "Piraeus": {"lat": 37.9385, "lon": 23.6947},
    "Marseille": {"lat": 43.2965, "lon": 5.3698},
    "Genoa": {"lat": 44.4056, "lon": 8.9463},
    "Valencia": {"lat": 39.4699, "lon": -0.3763},
    "Algeciras": {"lat": 36.1408, "lon": -5.4500},
    "Port Said": {"lat": 31.2653, "lon": 32.3019},
    "Suez": {"lat": 29.9668, "lon": 32.5498},
    "Jeddah": {"lat": 21.5433, "lon": 39.1728},
    "Bremen": {"lat": 53.0793, "lon": 8.8017},
    "Ningbo": {"lat": 29.8683, "lon": 121.5440},
    "Shenzhen": {"lat": 22.5431, "lon": 114.0579},
    "Guangzhou": {"lat": 23.1291, "lon": 113.2644},
    "Qingdao": {"lat": 36.0671, "lon": 120.3826},
    "Tianjin": {"lat": 39.0842, "lon": 117.2010},
    "Dalian": {"lat": 38.9140, "lon": 121.6147},
    "Xiamen": {"lat": 24.4798, "lon": 118.0819},
    "Yokohama": {"lat": 35.4437, "lon": 139.6380},
    "Kobe": {"lat": 34.6901, "lon": 135.1955},
    "Osaka": {"lat": 34.6937, "lon": 135.5023},
    "Nagoya": {"lat": 35.0844, "lon": 136.8991},
    "Port Klang": {"lat": 2.9988, "lon": 101.3933},
    "Ho Chi Minh": {"lat": 10.7626, "lon": 106.6602},
    "Karachi": {"lat": 24.8607, "lon": 67.0011},
    "Kolkata": {"lat": 22.5726, "lon": 88.3639},
    "Melbourne": {"lat": -37.8136, "lon": 144.9631},
    "Brisbane": {"lat": -27.4698, "lon": 153.0251},
    "Auckland": {"lat": -36.8485, "lon": 174.7633},
    "Honolulu": {"lat": 21.3099, "lon": -157.8581},
    "Panama City": {"lat": 8.9678, "lon": -79.5339},
    "Buenos Aires": {"lat": -34.6037, "lon": -58.3816},
    "Rio de Janeiro": {"lat": -22.9068, "lon": -43.1729},
    "Valparaiso": {"lat": -33.0472, "lon": -71.6127},
    "Callao": {"lat": -12.0564, "lon": -77.1278},
    "Cartagena": {"lat": 10.3910, "lon": -75.4794},
    "Lagos": {"lat": 6.4550, "lon": 3.3841},
    "Mombasa": {"lat": -4.0435, "lon": 39.6682},
    "Cape Town": {"lat": -33.9249, "lon": 18.4241},
    "Long Beach": {"lat": 33.7701, "lon": -118.2148},
    "Oakland": {"lat": 37.7947, "lon": -122.2806},
    "Seattle": {"lat": 47.6019, "lon": -122.3381},
    "Tacoma": {"lat": 47.2698, "lon": -122.4380},
    "Newark": {"lat": 40.6844, "lon": -74.1547},
    "Savannah": {"lat": 32.0835, "lon": -81.0998},
    "Charleston": {"lat": 32.7831, "lon": -79.9309},
    "Norfolk": {"lat": 36.9466, "lon": -76.3297},
    "Baltimore": {"lat": 39.2667, "lon": -76.5833},
    "New Orleans": {"lat": 29.9511, "lon": -90.0715},
    "Amsterdam": {"lat": 52.3667, "lon": 4.9000},
    "London": {"lat": 51.5074, "lon": -0.1278},
    "Abu Dhabi": {"lat": 24.4539, "lon": 54.3773},
    "Doha": {"lat": 25.2854, "lon": 51.5310},
    "La Spezia": {"lat": 44.1023, "lon": 9.8246},
    "Incheon": {"lat": 37.4563, "lon": 126.7052},
}

# Global Settings Store (In-memory for demo, could be DB/File)
SETTINGS = {
    "fuel_prices": {
        "HFO": 550,
        "MGO": 850,
        "LNG": 700
    },
    "default_speed": 12.0
}

HISTORY_FILE = "voyage_history.json"

def load_history():
    """Load voyage history safely"""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Failed to load history: {e}")
        return []

def save_history(entry):
    """Save a new voyage entry to history"""
    history = load_history()
    entry["timestamp"] = datetime.now().isoformat()
    # Keep last 50 entries
    history = [entry] + history[:49]
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"Failed to save history: {e}")

# --- API Endpoints for Dashboard Benchmarking ---

@app.get("/api/routes/history")
def get_history_api():
    return {"history": load_history()}

class HistoryEntry(BaseModel):
    ship_id: str
    start_port: str
    end_port: str
    savings_percent: float
    best_route_type: str = "balanced"

@app.post("/api/routes/history")
def add_history_api(entry: HistoryEntry):
    save_history(entry.dict())
    return {"status": "success"}

# --- Helper Functions ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of earth in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + \
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
        math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = R * c
    return d

def get_nearest_port(lat, lon):
    min_dist = float('inf')
    nearest = None
    for name, data in PORTS.items():
        dist = haversine(lat, lon, data["lat"], data["lon"])
        if dist < min_dist:
            min_dist = dist
            nearest = name
    return nearest, min_dist

# --- New Endpoints for Linus Enhancements ---

@app.get("/api/settings")
def get_settings():
    return SETTINGS

class SettingsUpdate(BaseModel):
    fuel_prices: dict
    default_speed: float

@app.post("/api/settings")
def update_settings(settings: SettingsUpdate):
    global SETTINGS
    SETTINGS["fuel_prices"] = settings.fuel_prices
    SETTINGS["default_speed"] = settings.default_speed
    return {"status": "updated", "settings": SETTINGS}

class NearestPortRequest(BaseModel):
    lat: float
    lon: float

@app.post("/api/ports/nearest")
def find_nearest_port_endpoint(req: NearestPortRequest):
    port_name, dist = get_nearest_port(req.lat, req.lon)
    return {"port": port_name, "distance_km": round(dist, 2)}

# LINUS TORVALDS PATCH: Added global-land-mask to stop ships driving on dirt.
# Also added stub for 52North WeatherRoutingTool integration.
try:
    from global_land_mask import globe
except ImportError:
    globe = None

def is_on_land(lat, lon):
    """Check if a point is on land using global-land-mask"""
    if globe is None:
        return False
    return globe.is_land(lat, lon)

def get_smart_waypoints(start_lat, start_lon, end_lat, end_lon, route_type):
    """
    Get key maritime waypoints to force different physical paths for different strategies.
    For example, Asia to Europe can go via Suez or Cape of Good Hope.
    """
    WAYPOINTS = {
        "MALACCA": (3.0, 100.0),
        "SRI_LANKA": (5.8, 80.5),
        "CAPE_GOOD_HOPE": (-35.0, 20.0),
        "ENGLISH_CHANNEL": (50.0, -2.0)
    }
    
    path = []
    
    is_asia_start = start_lon > 70 and -10 < start_lat < 40
    is_europe_end = end_lon < 15 and 35 < end_lat < 60
    
    if is_asia_start and is_europe_end:
        if route_type == "greenest": 
            # Force route around Africa to avoid emissions/canal fees
            path = [WAYPOINTS["MALACCA"], WAYPOINTS["SRI_LANKA"], WAYPOINTS["CAPE_GOOD_HOPE"], WAYPOINTS["ENGLISH_CHANNEL"]]
            
    # Add start/end
    full_path = [(start_lat, start_lon)] + path + [(end_lat, end_lon)]
    return full_path

import searoute

def generate_route(lat1, lon1, lat2, lon2, num_points=20, route_type="balanced"):
    """
    Generate ocean route avoiding land using the searoute pathfinding algorithm.
    """
    try:
        skeleton = get_smart_waypoints(lat1, lon1, lat2, lon2, route_type)
        final_points = []
        
        if route_type in ["fastest", "balanced"] or len(skeleton) <= 2:
            # Standard optimal shortest path
            route = searoute.searoute([lon1, lat1], [lon2, lat2])
            coords = route.get('geometry', {}).get('coordinates', [])
            final_points = [(lat, lon) for lon, lat in coords]
        else:
            # Connect the waypoints sequentially for alternative paths
            for i in range(len(skeleton) - 1):
                p1 = skeleton[i]
                p2 = skeleton[i+1]
                route = searoute.searoute([p1[1], p1[0]], [p2[1], p2[0]])
                coords = route.get('geometry', {}).get('coordinates', [])
                segment = [(lat, lon) for lon, lat in coords]
                
                if not final_points:
                    final_points.extend(segment)
                elif len(segment) > 1:
                    # Skip first point of segment to avoid duplicates
                    final_points.extend(segment[1:])
        
        if not final_points:
            return [(lat1, lon1), (lat2, lon2)]
            
        return final_points
    except Exception as e:
        import traceback
        print(f"Searoute routing failed: {e}")
        traceback.print_exc()
        return [(lat1, lon1), (lat2, lon2)]

# ---------------------------------------------------------
# NOTE: 52North WeatherRoutingTool Integration Point
# ---------------------------------------------------------
# To fully integrate https://github.com/52North/WeatherRoutingTool:
# 1. Install dependencies: pip install WeatherRoutingTool
# 2. Configure 'config.json' with vessel specs
# 3. Replace 'generate_route' with:
#    from WeatherRoutingTool.routeparams import RouteParams
#    route = RouteParams(start=(lat1, lon1), end=(lat2, lon2))
#    optimized_route = route.optimize(weather_file="grib_data.grb")
#    return optimized_route.get_points()
# ---------------------------------------------------------




def calculate_route_distance(route_points):
    """Calculate total distance of a route"""
    total = 0
    if not route_points or len(route_points) < 2:
        return 0
    for i in range(len(route_points) - 1):
        lat1, lon1 = route_points[i]
        lat2, lon2 = route_points[i + 1]
        total += haversine(lat1, lon1, lat2, lon2)
    return total

async def fetch_real_weather(lat, lon, api_key):
    """Fetch real-time weather from OpenWeatherMap"""
    if not api_key:
        return None
    try:
        async with httpx.AsyncClient() as client:
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
            resp = await client.get(url, timeout=5.0)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "wind_speed": data["wind"]["speed"] * 1.94384, # m/s to knots
                    "wind_direction": data["wind"]["deg"],
                    "temp": data["main"]["temp"],
                    "pressure": data["main"]["pressure"],
                    "description": data["weather"][0]["description"]
                }
    except Exception as e:
        print(f"Weather API failed: {e}")
    return None

def calculate_emissions(distance_km, speed_knots, vessel_type="container", vessel_size="medium", fuel_type="HFO"):
    """
    Enhanced calculation for CO2 emissions, Fuel Cost, and CII Rating.
    Includes edge case handling for zero distance/speed.
    """
    if distance_km <= 0 or speed_knots <= 0:
        return {
            "total_co2_tonnes": 0, "fuel_consumed_tonnes": 0, "voyage_days": 0,
            "estimated_cost_usd": 0, "cii_score": 0, "cii_rating": "N/A"
        }

    # 1. Determine DWT (Deadweight Tonnage) based on type/size
    dwt_table = {
        "container": {"small": 25000, "medium": 65000, "large": 150000},
        "tanker": {"small": 35000, "medium": 110000, "large": 300000},
        "bulk": {"small": 30000, "medium": 80000, "large": 180000}
    }
    dwt = dwt_table.get(vessel_type, dwt_table["container"]).get(vessel_size, 65000)

    # 2. Base consumption (tonnes/day at 12 knots)
    consumption_table = {
        "container": 140, "tanker": 110, "bulk": 90
    }
    base_consumption = consumption_table.get(vessel_type, 140)
    
    # Scale by size
    size_factor = {"small": 0.5, "medium": 1.0, "large": 1.6}.get(vessel_size, 1.0)
    consumption_per_day = base_consumption * size_factor

    # 3. Speed cube law (consumption ~ speed^3)
    speed_factor = (speed_knots / 12.0) ** 3
    daily_fuel = max(5.0, consumption_per_day * speed_factor) # Minimum idle fuel
    
    # 4. Voyage time (add 5% margin for maneuvering/weather)
    distance_nm = distance_km / 1.852
    hours = (distance_nm / speed_knots) * 1.05 
    days = hours / 24
    
    # 5. Total fuel
    total_fuel = daily_fuel * days
    
    # 6. CO2 Calculation (IMO EF)
    ef_fuel = {"HFO": 3.114, "MGO": 3.206, "LNG": 2.750}.get(fuel_type, 3.114)
    total_co2 = total_fuel * ef_fuel
    
    # 7. Fuel Cost
    price_per_ton = SETTINGS["fuel_prices"].get(fuel_type, 550)
    total_cost = total_fuel * price_per_ton
    
    # 8. CII Calculation (gCO2 / DWT-nm)
    cii_score = (total_co2 * 1_000_000) / (dwt * distance_nm) if distance_nm > 0 else 0
    
    # Rating logic
    if cii_score == 0: rating = "N/A"
    elif cii_score < 4.5: rating = "A"
    elif cii_score < 6.8: rating = "B"
    elif cii_score < 9.5: rating = "C"
    elif cii_score < 13.0: rating = "D"
    else: rating = "E"
    
    return {
        "total_co2_tonnes": round(total_co2, 2),
        "fuel_consumed_tonnes": round(total_fuel, 2),
        "voyage_days": round(days, 2),
        "estimated_cost_usd": round(total_cost, 2),
        "cii_score": round(cii_score, 2),
        "cii_rating": rating,
        "efficiency_index": round(100 / (1 + (cii_score/10)), 1)
    }

# Request Models
class RouteRequest(BaseModel):
    ship_id: str
    start: str
    end: str

class RouteCompareRequest(BaseModel):
    ship_id: str
    start_port: str
    end_port: str
    vessel_type: str = "container"
    vessel_size: str = "medium"
    fuel_type: str = "HFO"

class EmissionsRequest(BaseModel):
    distance_km: float
    speed_knots: float
    vessel_type: str = "container"
    vessel_size: str = "medium"
    fuel_type: str = "HFO"

# ========== API ENDPOINTS ==========

@app.get("/")
def root():
    return {
        "service": "NeoECDIS Maritime Intelligence API",
        "status": "running",
        "version": "2.0",
        "ports_loaded": len(PORTS)
    }

@app.get("/health")
def health():
    return {"status": "healthy", "ports": len(PORTS)}

@app.get("/api/ports/all")
def get_all_ports():
    """Get all available ports"""
    port_list = sorted(list(PORTS.keys()))
    return {"ports": port_list, "count": len(port_list)}

@app.get("/api/ports/search")
def search_ports(q: str):
    """Search ports by query"""
    results = [p for p in PORTS.keys() if q.lower() in p.lower()]
    return {"query": q, "results": results, "count": len(results)}

@app.post("/api/get_optimized_route/")
def get_optimized_route(request: RouteRequest):
    """Get optimized route between two ports"""
    if request.start not in PORTS:
        raise HTTPException(status_code=404, detail=f"Start port '{request.start}' not found")
    if request.end not in PORTS:
        raise HTTPException(status_code=404, detail=f"End port '{request.end}' not found")
    
    start = PORTS[request.start]
    end = PORTS[request.end]
    
    # Calculate ocean-aware route
    route_points = generate_route(start["lat"], start["lon"], end["lat"], end["lon"], 25, route_type="balanced")
    distance_km = calculate_route_distance(route_points)
    distance_nm = distance_km / 1.852
    
    avg_speed = SETTINGS.get("default_speed", 12.0)
    time_hours = distance_nm / avg_speed
    time_days = time_hours / 24
    
    return {
        "ship_id": request.ship_id,
        "start_port": request.start,
        "end_port": request.end,
        "optimized_route": route_points,
        "metadata": {
            "total_distance_km": round(distance_km, 2),
            "total_distance_nm": round(distance_nm, 2),
            "estimated_time_hours": round(time_hours, 2),
            "estimated_time_days": round(time_days, 2),
            "waypoints": len(route_points)
        }
    }

@app.post("/api/route/compare")
def compare_routes(request: RouteCompareRequest):
    """Compare 3 route strategies"""
    try:
        if request.start_port not in PORTS:
            raise HTTPException(status_code=404, detail=f"Start port not found")
        if request.end_port not in PORTS:
            raise HTTPException(status_code=404, detail=f"End port not found")
        if request.start_port == request.end_port:
            raise HTTPException(status_code=400, detail="Start and End ports cannot be the same")
        
        start = PORTS[request.start_port]
        end = PORTS[request.end_port]
        
        results = []
        
        for strategy, speed, color, route_type in [
            ("fastest", 15, "#ff6b6b", "fastest"),   # Suez - High Speed
            ("balanced", 12, "#4ECDC4", "balanced"), # Suez - Optimal Speed
            ("greenest", 10, "#95E38B", "greenest")  # Cape - Low Speed
        ]:
            # Generate route
            route_points = generate_route(
                start["lat"], start["lon"], 
                end["lat"], end["lon"], 
                25, 
                route_type=route_type
            )
            
            # Simulated weather for each route type (different regions have different averages)
            if "Green" in strategy or route_type == "greenest": # Longer routes like Cape
                avg_wind = round(random.uniform(14, 22), 1)
                avg_wave = round(random.uniform(2.5, 4.0), 1)
            else:
                avg_wind = round(random.uniform(8, 16), 1)
                avg_wave = round(random.uniform(1.2, 2.8), 1)
            
            # Calculate metrics
            distance_km = calculate_route_distance(route_points)
            distance_nm = distance_km / 1.852
            time_hours = distance_nm / speed
            time_days = time_hours / 24
            
            emissions = calculate_emissions(
                distance_km, 
                speed, 
                request.vessel_type, 
                request.vessel_size, 
                request.fuel_type
            )
            
            results.append({
                "route_name": strategy,
                "route_points": route_points,
                "color": color,
                "distance_km": round(distance_km, 0),
                "speed_knots": speed,
                "time_days": round(time_days, 1),
                "total_co2_tonnes": round(emissions["total_co2_tonnes"], 2),
                "fuel_tonnes": round(emissions["fuel_consumed_tonnes"], 2),
                "co2_savings_tonnes": 0.0, # Placeholder
                "co2_savings_percent": 0.0, # Placeholder
                "cii_rating": emissions["cii_rating"],
                "estimated_cost_usd": emissions["estimated_cost_usd"],
                "weather_summary": {
                    "avg_wind_kts": avg_wind,
                    "avg_wave_m": avg_wave
                }
            })

        # 2. Calculate Savings (Baseline = Highest CO2, usually Fastest)
        baseline_co2 = max(r["total_co2_tonnes"] for r in results)
        
        for r in results:
            savings = baseline_co2 - r["total_co2_tonnes"]
            r["co2_savings_tonnes"] = round(savings, 1)
            if baseline_co2 > 0:
                r["co2_savings_percent"] = round((savings / baseline_co2) * 100, 1)
             
        response_data = {
            "ship_id": request.ship_id,
            "start_port": request.start_port,
            "end_port": request.end_port,
            "routes": results,
            "recommendation": f"Balanced route recommended: saves {results[1]['co2_savings_tonnes']}t CO₂ ({results[1]['co2_savings_percent']}%) vs fastest route"
        }
        
        # Explicit serialization to prevent 500 errors from potential NaN/Inf
        from fastapi.encoders import jsonable_encoder
        encoded = jsonable_encoder(response_data)
        
        import json
        from fastapi.responses import Response
        json_str = json.dumps(encoded, allow_nan=False)
        return Response(content=json_str, media_type="application/json")

    except Exception as e:
        print("ERROR IN COMPARE:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/route/emissions")
def get_emissions(request: EmissionsRequest):
    """Calculate emissions for a route"""
    result = calculate_emissions(request.distance_km, request.speed_knots, request.vessel_type)
    return result

@app.get("/api/weather")
async def get_simple_weather(lat: float, lon: float, appid: Optional[str] = None):
    """
    Get weather at a point (fallback for smart navigator map-click).
    Matches the schema expected by Navigation.jsx map popup.
    """
    # Mock weather based on latitude
    lat_factor = abs(lat) / 90
    temp = round(28 - (lat_factor * 25) + random.uniform(-2, 2), 1)
    wind_speed = round(5 + (lat_factor * 10) + random.uniform(-3, 3), 1)
    pressure = round(1013 - (lat_factor * 20) + random.uniform(-5, 5), 0)
    
    return {
        "main": {"temp": temp, "pressure": pressure},
        "wind": {"speed": wind_speed, "deg": random.randint(0, 360)}
    }

@app.post("/api/route/weather-optimized")
def weather_route(request: RouteRequest):
    """Weather-optimized routing with simulated weather data"""
    if request.start not in PORTS or request.end not in PORTS:
        raise HTTPException(status_code=404, detail="Port not found")
    
    start = PORTS[request.start]
    end = PORTS[request.end]
    
    route_points = generate_route(start["lat"], start["lon"], end["lat"], end["lon"], 25, route_type="balanced")
    distance_km = calculate_route_distance(route_points)
    
    vessel_speed = 12.0
    
    # Realistic weather simulation based on route geography
    import random
    import math
    segments = []
    
    for i in range(5):
        # Get midpoint of this segment
        segment_start = math.floor((len(route_points) / 5) * i)
        segment_end = math.floor((len(route_points) / 5) * (i + 1))
        mid_idx = (segment_start + segment_end) // 2
        
        if mid_idx < len(route_points):
            lat, lon = route_points[mid_idx]
        else:
            lat, lon = route_points[-1]
        
        # Latitude-based weather patterns
        lat_factor = abs(lat) / 90  # 0 at equator, 1 at poles
        
        # Wind speed increases with latitude (trade winds vs westerlies)
        base_wind = 5 + (lat_factor * 12) + random.uniform(-2, 2)
        wind_speed = max(3, min(30, base_wind))
        
        # Wave height correlates with wind
        wave_height = 0.3 + (wind_speed / 12) + random.uniform(-0.3, 0.3)
        wave_height = max(0.2, min(6.0, wave_height))
        
        # Wind direction (prevailing patterns)
        if abs(lat) < 30:  # Trade winds (easterlies)
            wind_direction = 90 + random.randint(-30, 30)
        elif abs(lat) > 60:  # Polar easterlies  
            wind_direction = 90 + random.randint(-40, 40)
        else:  # Westerlies
            wind_direction = 270 + random.randint(-40, 40)
        wind_direction = wind_direction % 360
        
        # Temperature decreases with latitude
        temperature = 28 - (lat_factor * 25) + random.uniform(-3, 3)
        
        # Conditions based on wind speed
        if wind_speed < 10:
            conditions = "calm"
            danger_level = 0.1
        elif wind_speed < 18:
            conditions = "moderate"
            danger_level = 0.4
        elif wind_speed < 25:
            conditions = "rough"
            danger_level = 0.7
        else:
            conditions = "extreme"
            danger_level = 1.0
        
        # Speed factor based on weather
        speed_factor = max(0.65, 1.0 - (wind_speed - 10) / 60)
        if wave_height > 3.0:
            speed_factor *= 0.95
        
        segments.append({
            "segment": i + 1,
            "distance_km": round(distance_km / 5, 2),
            "adjusted_speed": round(vessel_speed * speed_factor, 2),
            "latitude": round(lat, 2),
            "longitude": round(lon, 2),
            "danger_level": danger_level,
            "weather": {
                "wind_speed": round(wind_speed, 1),
                "wind_direction": wind_direction,
                "wave_height": round(wave_height, 1),
                "temperature": round(temperature, 1),
                "conditions": conditions
            }
        })
    
    return {
        "ship_id": request.ship_id,
        "start_port": request.start,
        "end_port": request.end,
        "total_distance_km": round(distance_km, 2),
        "route_points": route_points,
        "segments": segments,
        "weather_impact": {
            "speed_efficiency": 85,
            "time_difference_vs_simple": 4.5
        }
    }


# ---------------------------------------------------------
# Linus Note: Real-time ship traffic simulation
# In production, this would connect to an AIS stream (Spire, MarineTraffic).
# ---------------------------------------------------------
@app.get("/api/ship-traffic")
def get_ship_traffic():
    """Simulate some ships in the Indian Ocean / SE Asia"""
    try:
        ships = []
        
        # Consistent set of vessel names for higher fidelity simulation
        VESSEL_NAMES = [
            "Deep Horizon", "Ocean Explorer", "Arctic Star", "Global Carrier",
            "Pacific Voyager", "Blue Wave", "Sea Titan", "Ever Fortune",
            "Maersk Pioneer", "COSCO Excellence", "Norwegian Jade", "Singapore Spirit"
        ]
        
        # Base locations for different clusters
        BASES = [
            (6.0, 80.0),   # Sri Lanka
            (1.0, 104.0),  # Singapore
            (25.0, 55.0),  # Dubai/Persian Gulf
            (12.0, 45.0)   # Aden/Red Sea
        ]
        
        for i in range(25):
            base_lat, base_lon = random.choice(BASES)
            lat = base_lat + random.uniform(-6, 6)
            lon = base_lon + random.uniform(-10, 10)
            
            # Use global-land-mask if available
            if is_on_land(lat, lon):
                lat -= 1.5 # Nudge offshore
            
            # Determine destination for the "Command Center" planning feature
            potential_destinations = [p for p in PORTS.keys() if p != "Singapore"]
            dest = random.choice(potential_destinations) if potential_destinations else "Rotterdam"
                
            ships.append({
                "mmsi": 412000000 + i,
                "name": VESSEL_NAMES[i % len(VESSEL_NAMES)],
                "lat": round(lat, 4),
                "lon": round(lon, 4),
                "sog": round(random.uniform(8.0, 19.0), 1),
                "cog": round(random.uniform(0, 360), 0),
                "status": random.choice(["Underway", "Slow Steaming", "Operational"]),
                "destination_hint": dest,
                "vessel_type": random.choice(["container", "tanker", "bulk"]),
                "vessel_size": random.choice(["small", "medium", "large"])
            })
            
        # Calculate Fleet Summary for Dashboard
        total_sog = sum(s["sog"] for s in ships)
        avg_sog = total_sog / len(ships) if ships else 0
        
        # Emissions aggregation (Simplified approximation)
        # Assuming HFO container mid-size as baseline for fleet stats
        fleet_co2_daily = sum(
            calculate_emissions(200, s["sog"], s["vessel_type"], s["vessel_size"])["total_co2_tonnes"] 
            for s in ships
        ) * 5 # Scale up to daily estimate

        return {
            "ships": ships,
            "summary": {
                "active_units": len(ships),
                "avg_fleet_speed": round(avg_sog, 1),
                "estimated_fleet_co2_daily": round(fleet_co2_daily, 2),
                "system_load": 22.5 # Simulated load
            }
        }
    except Exception as e:
        print(f"Error in ship traffic: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
