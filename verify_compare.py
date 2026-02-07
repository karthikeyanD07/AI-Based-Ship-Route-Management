import requests
import json

URL = "http://localhost:8000/api/route/compare"

payload = {
    "ship_id": "MMSI-123456789",
    "start_port": "Singapore",
    "end_port": "Rotterdam",
    "vessel_type": "container",
    "vessel_size": "medium",
    "fuel_type": "HFO"
}

try:
    print(f"🚀 Sending request to {URL}...")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(URL, json=payload)
    
    print(f"📡 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Success!")
        print(f"📊 Recommendation: {data.get('recommendation')}")
        print(f"🛣️ Routes Generated: {len(data.get('routes', []))}")
        for r in data.get('routes', []):
            print(f"   - {r['route_name']}: {r['total_co2_tonnes']}t CO2")
    else:
        print("❌ Failed!")
        print(response.text)

except Exception as e:
    print(f"🔥 Error: {e}")
