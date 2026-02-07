import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def check_endpoint(method, endpoint, payload=None):
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url)
        else:
            response = requests.post(url, json=payload)
        
        status = response.status_code
        if status == 200:
            print(f"✅ {method} {endpoint}: OK ({len(response.content)} bytes)")
            return True
        else:
            print(f"❌ {method} {endpoint}: FAILED ({status}) - {response.text[:100]}")
            return False
    except Exception as e:
        print(f"❌ {method} {endpoint}: ERROR - {str(e)}")
        return False

print("🔍 Starting Backend Connectivity Check...")

# 1. Health/Root
check_endpoint("GET", "/")

# 2. Ports
check_endpoint("GET", "/api/ports/all")

# 3. Ship Traffic
check_endpoint("GET", "/api/ship-traffic")

# 4. Settings
check_endpoint("GET", "/api/settings")

# 5. Route Comparison (The broken one?)
payload = {
    "ship_id": "MMSI-123456789",
    "start_port": "Singapore",
    "end_port": "Rotterdam",
    "vessel_type": "container",
    "vessel_size": "medium"
}
if check_endpoint("POST", "/api/route/compare", payload):
    print("   -> Comparison functionality seems reachable.")
else:
    print("   -> ⚠️ Comparison endpoint is failing!")

print("🏁 Check Complete.")
