import requests
import json

url = "http://localhost:5001/api/scrape"
payload = {
    "url": "https://www.amazon.in/WOOYNEX-Magazines-Entryway-Antic-Burning/dp/B0D22VRJ63"
}
headers = {'Content-Type': 'application/json'}

try:
    print(f"Sending request to {url}...")
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Reviews count: {data.get('count')}")
        reviews = data.get('reviews', [])
        if reviews:
            print("First review sample:")
            print(json.dumps(reviews[0], indent=2))
        else:
            print("No reviews in response.")
    else:
        print("Error Response:")
        print(response.text)
        
except Exception as e:
    print(f"Request failed: {e}")
