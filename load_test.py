"""Load testing script using locust."""
from locust import HttpUser, task, between
import random


class ShipRouteUser(HttpUser):
    """Simulated user for load testing."""
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login on start."""
        # Register and login
        username = f"loadtest_{random.randint(1000, 9999)}"
        self.client.post(
            "/api/v1/auth/register",
            json={
                "username": username,
                "email": f"{username}@test.com",
                "password": "testpass123"
            }
        )
        response = self.client.post(
            "/api/v1/auth/login",
            data={"username": username, "password": "testpass123"}
        )
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.headers = {}
    
    @task(3)
    def get_ships(self):
        """Get ship traffic."""
        self.client.get("/api/v1/ships", headers=self.headers)
    
    @task(1)
    def get_weather(self):
        """Get weather data."""
        lat = random.uniform(-90, 90)
        lon = random.uniform(-180, 180)
        self.client.get(f"/api/v1/weather?lat={lat}&lon={lon}", headers=self.headers)
    
    @task(1)
    def optimize_route(self):
        """Optimize route."""
        self.client.post(
            "/api/v1/routes/optimize",
            json={
                "ship_id": str(random.randint(100000000, 999999999)),
                "start": "Port A",
                "end": "Port B"
            },
            headers=self.headers
        )
    
    @task(1)
    def health_check(self):
        """Health check."""
        self.client.get("/health")
