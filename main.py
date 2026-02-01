from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import random
import asyncio
import os
import math
import json
import numpy as np

app = FastAPI()

# ✅ Enable CORS for frontend (React/Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Load AIS Data from `trip9.csv`
csv_file = "trip9.csv"

if not os.path.exists(csv_file):
    raise FileNotFoundError(f"🚨 Error: CSV file '{csv_file}' not found!")

ais_data = pd.read_csv(csv_file)

# ✅ Standardize Column Names
column_mapping = {
    "ID": "MMSI",
    "Latitude": "lat",
    "Longitude": "lon",
    "Speed": "sog",
    "Course": "cog",
    "ShipStatus": "status"
}
ais_data.rename(columns={k: v for k, v in column_mapping.items() if k in ais_data.columns}, inplace=True)

# ✅ Ensure Required Columns Exist
required_columns = {"MMSI", "lat", "lon", "sog", "cog", "status"}
missing_columns = required_columns - set(ais_data.columns)

if missing_columns:
    raise ValueError(f"🚨 CSV file is missing required columns: {missing_columns}")

# ✅ Fix NaN Values & Invalid Data
ais_data.replace([np.nan, np.inf, -np.inf], 0, inplace=True)  # Replace NaN, inf, -inf with 0
ais_data.fillna({
    "sog": 0.0,
    "cog": 0.0,
    "status": "Unknown",
    "lat": 0.0,
    "lon": 0.0
}, inplace=True)

# Convert all numeric columns to `float`
for col in ["sog", "cog", "lat", "lon"]:
    ais_data[col] = pd.to_numeric(ais_data[col], errors="coerce").fillna(0.0)

# ✅ Store ship positions globally
ship_positions = {}

# ✅ Function to check if a ship is in water
def is_ocean(lat, lon):
    """Ensures ships stay on water and not land."""
    if abs(lat) > 60:  # Arctic/Antarctic (Land)
        return False
    if (-20 < lat < 30 and -20 < lon < 50):  # Africa (Land)
        return False
    if (30 < lat < 60 and -130 < lon < -60):  # USA/Canada (Land)
        return False
    return True

# ✅ Initialize Ships at Dataset Positions
for _, row in ais_data.iterrows():
    lat, lon = row["lat"], row["lon"]

    # Ensure ship starts in water
    if not is_ocean(lat, lon):
        lat += 0.5  # Move slightly to water
        lon += 0.5

    ship_positions[row["MMSI"]] = {
        "latitude": lat,
        "longitude": lon,
        "sog": row["sog"],
        "cog": row["cog"],
        "status": row["status"]
    }

# ✅ Move Ships Based on Dataset (Speed & Direction)
def move_ship(mmsi):
    """Moves a ship based on its SOG (speed) and COG (direction)."""
    ship = ship_positions[mmsi]
    sog = ship["sog"]
    cog = ship["cog"]

    # 🚢 If ship is moored (speed = 0), do not move
    if sog == 0:
        return  

    # Convert speed from knots to movement scale
    distance = sog * 0.0002  # Adjusted for better movement

    # Convert course to radians
    angle = math.radians(cog)

    # Compute new lat/lon
    lat_change = distance * math.cos(angle)
    lon_change = distance * math.sin(angle)

    new_lat = ship["latitude"] + lat_change
    new_lon = ship["longitude"] + lon_change

    # ✅ Ensure ship stays in the ocean
    if is_ocean(new_lat, new_lon):
        ship_positions[mmsi]["latitude"] = new_lat
        ship_positions[mmsi]["longitude"] = new_lon
    else:
        # If ship would go on land, adjust course slightly
        ship_positions[mmsi]["cog"] += random.uniform(-10, 10)

# ✅ Background Task: Move Ships Every 3 Seconds
async def update_ship_positions():
    """Continuously updates ship positions based on speed and direction."""
    while True:
        for mmsi in ship_positions:
            move_ship(mmsi)
        await asyncio.sleep(3)  # ✅ Update every 3 seconds

# ✅ Start Background Task on Startup
@app.on_event("startup")
async def start_background_task():
    asyncio.create_task(update_ship_positions())

# ✅ API Endpoint: Get All Ships' Positions
@app.get("/ship-traffic")
def get_ship_traffic():
    ships = []
    for i, mmsi in enumerate(ship_positions):
        if i >= 10:  # Fetch only 10 ships for performance
            break
        ship_data = ais_data[ais_data["MMSI"] == mmsi].iloc[0].to_dict()

        # ✅ Ensure JSON-safe values (convert NaN and Inf to valid numbers)
        for key, value in ship_data.items():
            if isinstance(value, float) and (np.isnan(value) or np.isinf(value)):
                ship_data[key] = 0.0  # Replace NaN/Inf with 0.0

        ship_data["latitude"] = float(ship_positions[mmsi]["latitude"])
        ship_data["longitude"] = float(ship_positions[mmsi]["longitude"])
        ship_data["status"] = ship_positions[mmsi]["status"]
        ships.append(ship_data)

    return json.loads(json.dumps({"ships": ships}, default=str))  # ✅ Convert safely to JSON

# ✅ API Endpoint: Get a Specific Ship's Position
@app.get("/ship/{mmsi}")
def get_ship_by_mmsi(mmsi: str):
    if mmsi not in ship_positions:
        raise HTTPException(status_code=404, detail="Ship not found")

    ship_data = ais_data[ais_data["MMSI"] == mmsi]
    if ship_data.empty:
        raise HTTPException(status_code=404, detail="Ship data not found")

    ship_info = ship_data.iloc[0].to_dict()
    ship_info["latitude"] = ship_positions[mmsi]["latitude"]
    ship_info["longitude"] = ship_positions[mmsi]["longitude"]
    ship_info["status"] = ship_positions[mmsi]["status"]

    return ship_info

# ✅ Home Route
@app.get("/")
def home():
    return {"message": "AIS Ship Tracking API is running with real-time movement"}
