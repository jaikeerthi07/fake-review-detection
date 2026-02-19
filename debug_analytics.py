import requests
import json

try:
    # Check analytics
    r = requests.get('http://localhost:5001/api/analytics')
    print(f"Status: {r.status_code}")
    data = r.json()
    print("Full response:", json.dumps(data, indent=2)[:500])
except Exception as e:
    print(f"Error: {e}")
