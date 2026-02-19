import requests
import json

url = "http://localhost:5001/api/scrape"
payload = {
    "url": "https://www.ubuy.co.in/product/R1K5YEMBM-hand-warmers-rechargerable-2-pack-4000mah-electric-handwarmers-reusable-portable-pocket-heater-gifts-for-women-men"
}

try:
    print(f"Sending POST request to {url} with payload: {payload['url']}")
    response = requests.post(url, json=payload)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success! Reviews count: {len(data.get('reviews', []))}")
        print("Sample Review:")
        if data.get('reviews'):
            print(data['reviews'][0][:100] + "...")
    else:
        print("Error:")
        print(response.text)
except Exception as e:
    print(f"Request failed: {e}")
