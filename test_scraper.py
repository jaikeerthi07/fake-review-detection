import requests
import json

url = 'http://localhost:5001/api/scrape'
payload = {'url': 'https://www.amazon.in/dp/B0BZCSNTT4'}

try:
    print(f"Testing scraper with URL: {payload['url']}")
    response = requests.post(url, json=payload)
    
    print(f"Status Code: {response.status_code}")
    print("Response:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
