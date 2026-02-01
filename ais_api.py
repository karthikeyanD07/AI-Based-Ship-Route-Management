from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import random
import asyncio
import os
import math
import numpy as np
from functools import lru_cache

# ✅ Create FastAPI App
app = FastAPI()

# ✅ Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change this for security)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

router = APIRouter()

# ✅ Load AIS Data from `trip9.csv`
csv_file = "final_ship_routes.csv"

if not os.path.exists(csv_file):
    raise FileNotFoundError(f"🚨 Error: CSV file '{csv_file}' not found!")

ais_data = pd.read_csv(csv_file)

# ✅ Column Mapping Based on Your CSV File
column_mapping = {
    "MMSI": "MMSI",
    "LAT": "lat",
    "LON": "lon",
    "SOG": "sog",
    "COG": "cog",
    "Status": "status"
}
ais_data.rename(columns=column_mapping, inplace=True)

# ✅ Add Missing Columns
ais_data["cog"] = ais_data.get("cog", np.random.uniform(0, 360, len(ais_data)))
ais_data["status"] = ais_data.get("status", "Unknown")

# ✅ Ensure Required Columns Exist
required_columns = {"MMSI", "lat", "lon", "sog", "cog", "status"}
missing_columns = required_columns - set(ais_data.columns)

if missing_columns:
    raise ValueError(f"🚨 CSV file is missing required columns: {missing_columns}")

# ✅ Fix NaN Values & Invalid Data
ais_data.fillna({
    "sog": 0.0,
    "cog": random.uniform(0, 360),  # Assign a random course if missing
    "status": "Unknown",
    "lat": 0.0,
    "lon": 0.0
}, inplace=True)

# Convert all numeric columns to `float`
for col in ["sog", "cog", "lat", "lon"]:
    ais_data[col] = pd.to_numeric(ais_data[col], errors="coerce").fillna(0.0)

# ✅ Select 10 Unique Ships
num_ships = min(500, len(ais_data["MMSI"].unique()))
selected_ships = ais_data["MMSI"].drop_duplicates().sample(n=num_ships, random_state=42).tolist()

# ✅ Store 10 ship positions globally
ship_positions = {}

# ✅ Function to Check if a Ship is in Water
def is_ocean(lat, lon):
    """Ensures ships stay on water and not land."""
    if abs(lat) > 60:  # Arctic/Antarctic (Land)
        return False
    if (-20 < lat < 30 and -20 < lon < 50):  # Africa (Land)
        return False
    if (30 < lat < 60 and -130 < lon < -60):  # USA/Canada (Land)
        return False
    return True

# ✅ Initialize 10 Ships at Dataset Positions
for _, row in ais_data[ais_data["MMSI"].isin(selected_ships)].iterrows():
    lat, lon = row["lat"], row["lon"]

    # Ensure ship starts in water
    if not is_ocean(lat, lon):
        lat += 0.5
        lon += 0.5

    # Assign a random speed if missing
    sog = row["sog"]
    if sog == 0:
        sog = random.uniform(5, 15)

    ship_positions[row["MMSI"]] = {
        "latitude": lat,
        "longitude": lon,
        "sog": sog,
        "cog": row["cog"],
        "status": row["status"]
    }

# ✅ Function to Move Ships
def move_ship(mmsi):
    """Moves a ship based on its SOG (speed) and COG (direction)."""
    ship = ship_positions[mmsi]
    old_lat, old_lon = ship["latitude"], ship["longitude"]
    
    sog = ship["sog"]
    cog = ship["cog"]

    if sog == 0:
        return  # Do not move if speed is 0

    distance = sog * 0.0002  # Adjust speed for visualization
    angle = math.radians(cog)

    lat_change = distance * math.cos(angle)
    lon_change = distance * math.sin(angle)

    new_lat = old_lat + lat_change
    new_lon = old_lon + lon_change

    # Ensure ship stays in the ocean
    if is_ocean(new_lat, new_lon):
        ship_positions[mmsi]["latitude"] = new_lat
        ship_positions[mmsi]["longitude"] = new_lon
    else:
        ship_positions[mmsi]["cog"] += random.uniform(-10, 10)  # Change direction

# ✅ Background Task: Move Ships
async def update_ship_positions():
    """Continuously updates ship positions every 3 seconds."""
    while True:
        for mmsi in ship_positions:
            move_ship(mmsi)
        await asyncio.sleep(3)

# ✅ API Endpoint: Get 10 Ships' Positions
@router.get("/ship-traffic")
def get_ship_traffic():
    """Returns real-time positions of 10 ships."""
    ships = []
    for mmsi, ship in ship_positions.items():
        ships.append({
            "MMSI": mmsi,
            "latitude": float(ship["latitude"]),
            "longitude": float(ship["longitude"]),
            "sog": float(ship["sog"]),
            "cog": float(ship["cog"]),
            "status": ship["status"]
        })

    return {"ships": ships}

# ✅ API Endpoint: Get a Specific Ship's Position
@router.get("/ship/{mmsi}")
def get_ship_by_mmsi(mmsi: str):
    """Returns real-time position of a specific ship."""
    try:
        mmsi = int(mmsi)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid MMSI format")

    if mmsi not in ship_positions:
        raise HTTPException(status_code=404, detail="Ship not found")

    ship = ship_positions[mmsi]
    return {
        "MMSI": mmsi,
        "latitude": ship["latitude"],
        "longitude": ship["longitude"],
        "sog": ship["sog"],
        "cog": ship["cog"],
        "status": ship["status"]
    }

# ✅ Simple Root
@app.get("/")
def root():
    return {"message": "AIS Ship API running"}

# ✅ Start Background Task
@app.on_event("startup")
async def start_moving_ships():
    asyncio.create_task(update_ship_positions())

class OptimizeRouteRequest(BaseModel):
    ship_id: str
    start: str
    end: str


# Simple preset of port coordinates to mirror frontend choices
PORT_COORDS = {
    "Port A": (33.7405, -118.2519),
    "Port B": (40.6728, -74.1536),
    "Port C": (29.7305, -95.0892),
    "Port D": (25.7785, -80.1826),
    "Port E": (32.0835, -81.0998),
    "Port F": (47.6019, -122.3381),
}


def interpolate_route(start_lat: float, start_lon: float, end_lat: float, end_lon: float, steps: int = 20):
    """Generate a simple interpolated polyline between two coordinates."""
    if steps < 2:
        return [[start_lat, start_lon], [end_lat, end_lon]]
    lat_step = (end_lat - start_lat) / (steps - 1)
    lon_step = (end_lon - start_lon) / (steps - 1)
    route = []
    for i in range(steps):
        route.append([start_lat + i * lat_step, start_lon + i * lon_step])
    return route


def great_circle_route(start_lat: float, start_lon: float, end_lat: float, end_lon: float, steps: int = 120):
    """Generate a great-circle path between two points (lat/lon degrees)."""
    import math
    # convert to radians
    φ1 = math.radians(start_lat)
    λ1 = math.radians(start_lon)
    φ2 = math.radians(end_lat)
    λ2 = math.radians(end_lon)

    Δ = 2 * math.asin(math.sqrt(
        math.sin((φ2-φ1)/2)**2 + math.cos(φ1)*math.cos(φ2)*math.sin((λ2-λ1)/2)**2
    ))
    if Δ == 0:
        return [[start_lat, start_lon]]

    route = []
    for i in range(steps+1):
        f = i/steps
        A = math.sin((1-f)*Δ) / math.sin(Δ)
        B = math.sin(f*Δ) / math.sin(Δ)
        x = A*math.cos(φ1)*math.cos(λ1) + B*math.cos(φ2)*math.cos(λ2)
        y = A*math.cos(φ1)*math.sin(λ1) + B*math.cos(φ2)*math.sin(λ2)
        z = A*math.sin(φ1) + B*math.sin(φ2)
        φ = math.atan2(z, math.sqrt(x*x + y*y))
        λ = math.atan2(y, x)
        route.append([math.degrees(φ), math.degrees(λ)])
    return route


def nudge_point_to_ocean(lat: float, lon: float, max_iters: int = 50):
    """Push a point slightly toward nearby ocean using coarse continental heuristics."""
    if is_ocean(lat, lon):
        return lat, lon

    cur_lat, cur_lon = lat, lon
    for _ in range(max_iters):
        # Americas heuristic: continental center around -95 lon
        if 7 < cur_lat < 84 and -168 < cur_lon < -52:
            cur_lon += 0.5 if cur_lon > -95 else -0.5
        # Africa heuristic: push east or west away from center ~15 lon
        elif -35 < cur_lat < 37 and -18 < cur_lon < 52:
            cur_lon += 0.5 if cur_lon < 15 else -0.5
        # Eurasia heuristic: push south toward seas or east/west to edges
        elif 5 < cur_lat < 77 and -10 < cur_lon < 180:
            cur_lat -= 0.3  # bias south toward Mediterranean/Indian oceans
            cur_lon += 0.3
        # Australia heuristic
        elif -45 < cur_lat < -10 and 112 < cur_lon < 155:
            cur_lon += 0.4
        else:
            # Generic small drift east
            cur_lon += 0.3

        if is_ocean(cur_lat, cur_lon):
            break
    return cur_lat, cur_lon


def ocean_safe_route(points: list[list[float]]):
    """Apply ocean nudging to a list of [lat, lon] points."""
    corrected = []
    for lat, lon in points:
        nlat, nlon = nudge_point_to_ocean(lat, lon)
        corrected.append([nlat, nlon])
    return corrected


def build_maritime_route(start_lat: float, start_lon: float, end_lat: float, end_lon: float):
    """Construct an ocean-biased route using heuristic maritime waypoints for the Americas."""
    waypoints = []
    # South of Florida waypoint to avoid cutting across land when going east-west in US
    florida_south = (23.5, -80.0)
    # Yucatan channel area
    yucatan = (21.5, -86.5)
    # Caribbean mid
    caribbean_mid = (16.5, -75.0)
    # Panama Canal Atlantic entrance (Colon)
    panama_atl = (9.36, -79.90)
    # Panama Canal Pacific exit (Balboa)
    panama_pac = (8.95, -79.55)
    # Baja south
    baja_south = (22.9, -109.9)

    # Decide waypoint chain based on general longitudes
    segments = []
    if start_lon < -95 and end_lon > -80:
        # Gulf -> East Coast: go south of Florida
        waypoints = [florida_south]
    elif start_lon > -80 and end_lon < -95:
        # East Coast -> Gulf: go south of Florida
        waypoints = [florida_south]
    elif start_lon < -95 and end_lon < -120:
        # Gulf -> Pacific: via Panama Canal then up Baja
        waypoints = [yucatan, panama_atl, panama_pac, baja_south]
    elif start_lon < -120 and end_lon > -95:
        # Pacific -> Gulf/East: via Baja down to Panama then Caribbean
        waypoints = [baja_south, panama_pac, panama_atl, caribbean_mid]

    # Build segments through waypoints
    prev = (start_lat, start_lon)
    for wp in waypoints:
        segments.append(interpolate_route(prev[0], prev[1], wp[0], wp[1], steps=40))
        prev = wp
    segments.append(interpolate_route(prev[0], prev[1], end_lat, end_lon, steps=40))

    # Flatten and ocean-correct
    flat = [pt for seg in segments for pt in seg]
    return ocean_safe_route(flat)


@lru_cache(maxsize=512)
def cached_route(start_lat: float, start_lon: float, end_lat: float, end_lon: float):
    # Prefer great-circle for efficiency, then bias with maritime waypoints if needed
    gc = great_circle_route(start_lat, start_lon, end_lat, end_lon, steps=160)
    gc_ocean = ocean_safe_route(gc)
    return gc_ocean


@router.post("/get_optimized_route/")
def get_optimized_route(payload: OptimizeRouteRequest):
    """
    Returns a naive optimized route polyline between two named ports.
    The frontend expects a list of [lat, lon] points under `optimized_route`.
    """
    if payload.start not in PORT_COORDS or payload.end not in PORT_COORDS:
        raise HTTPException(status_code=400, detail="Unknown start or end port")

    start_lat, start_lon = PORT_COORDS[payload.start]
    end_lat, end_lon = PORT_COORDS[payload.end]

    # Construct a cached great-circle ocean-safe route
    polyline = cached_route(start_lat, start_lon, end_lat, end_lon)
    return {"ship_id": payload.ship_id, "optimized_route": polyline}

# ✅ Expose the same endpoint at app-level to avoid router order edge-cases
@app.post("/get_optimized_route/")
def get_optimized_route_app(payload: OptimizeRouteRequest):
    return get_optimized_route(payload)

# ✅ Include Router in the App (after routes are defined)
app.include_router(router)
