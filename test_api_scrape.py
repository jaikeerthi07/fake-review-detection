import requests
import json

def test_api():
    url = "http://localhost:5001/api/scrape"
    payload = {"url": "https://www.nykaa.com/maybelline-new-york-super-stay-matte-ink-liquid-lipstick/p/231122"}
    headers = {"Content-Type": "application/json"}
    
    print(f"Sending request to {url}...")
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print("Response Body:")
        print(response.text)
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    test_api()
