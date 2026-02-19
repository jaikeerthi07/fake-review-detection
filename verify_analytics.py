import requests
import json

try:
    response = requests.get('http://localhost:5001/api/analytics')
    if response.status_code == 200:
        data = response.json()
        print("Analytics Data fetched successfully.")
        print(json.dumps(data.get('rating_distribution', []), indent=2))
    else:
        print(f"Failed: {response.status_code} - {response.text}")
except Exception as e:
    print(f"Error: {e}")
