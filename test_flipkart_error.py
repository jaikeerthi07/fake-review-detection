import requests

url = 'http://localhost:5001/api/scrape'
payload = {'url': 'https://www.flipkart.com/test'}

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
