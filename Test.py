from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import heapq
import random
import geopy.distance  # To calculate real-world distances

app = FastAPI()

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust for your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Port locations (latitude, longitude) near the sea
port_locations = {
    "Port A": (33.7405, -118.2519),  # Los Angeles
    "Port B": (40.6728, -74.1536),   # New York
    "Port C": (29.7305, -95.0892),   # Houston
    "Port D": (25.7785, -80.1826),   # Miami
    "Port E": (32.0835, -81.0998),   # Savannah
    "Port F": (47.6019, -122.3381)   # Seattle
}

# Simulated function to check if a coordinate is water
def is_water(lat, lon):
    """ Placeholder function: In production, use real GIS APIs """
    return True  # Assume all locations are water for now

# Get dynamic neighbors (simulate moving only on water)
def get_dynamic_neighbors(lat, lon):
    """ Generate possible moves (e.g., nearby water locations) and filter out land. """
    step_size = 1.0  # Adjust step size for movement
    possible_moves = [
        (lat + step_size, lon), (lat - step_size, lon),
        (lat, lon + step_size), (lat, lon - step_size)
    ]
    return [(lat, lon) for lat, lon in possible_moves if is_water(lat, lon)]

# Dynamic Dijkstra Algorithm for Route Optimization
def dijkstra_dynamic(start, end):
    pq = []
    heapq.heappush(pq, (0, start, []))
    visited = set()

    while pq:
        cost, (lat, lon), path = heapq.heappop(pq)

        if (lat, lon) in visited:
            continue
        visited.add((lat, lon))

        path = path + [(lat, lon)]

        if geopy.distance.geodesic((lat, lon), end).km < 1:  # Closer threshold for accuracy
            return path

        for neighbor in get_dynamic_neighbors(lat, lon):
            if neighbor not in visited:
                total_cost = cost + random.randint(1, 10)  # Simulate dynamic cost
                heapq.heappush(pq, (total_cost, neighbor, path))

    return []  # No path found

# Request Model
class RouteRequest(BaseModel):
    ship_id: str
    start: str
    end: str

@app.post("/get_optimized_route/")
def get_optimized_route(data: RouteRequest):
    if data.start not in port_locations or data.end not in port_locations:
        return {"error": "Invalid port selection"}
    
    start_coords = port_locations[data.start]
    end_coords = port_locations[data.end]

    optimized_route = dijkstra_dynamic(start_coords, end_coords)

    # Ensure proper format for React Leaflet
    formatted_route = [[lat, lon] for lat, lon in optimized_route]

    return {"ship_id": data.ship_id, "optimized_route": formatted_route}
