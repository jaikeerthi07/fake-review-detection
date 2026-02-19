import requests
import time
import json
import sys
import os

APIFY_TOKEN = os.getenv('APIFY_TOKEN', 'YOUR_APIFY_TOKEN_HERE')
url = "https://www.amazon.com/Alli-Diet-Weight-Loss-Supplement-Pills/dp/B000TGS3WA"

print("--- Debugging Apify Connection ---")

# 1. Check Internet
try:
    print("Checking internet...")
    requests.get("https://www.google.com", timeout=5)
    print("Internet OK.")
except Exception as e:
    print(f"Internet Check Failed: {e}")
    sys.exit(1)

# 2. Check Token
try:
    print("Checking Apify Token...")
    user_url = f"https://api.apify.com/v2/users/me?token={APIFY_TOKEN}"
    res = requests.get(user_url, timeout=10)
    if res.status_code == 200:
        print(f"Token OK. User: {res.json()['data']['username']}")
    else:
        print(f"Token Error: {res.status_code} - {res.text}")
        sys.exit(1)
except Exception as e:
    print(f"Token Check Failed: {e}")
    sys.exit(1)

# 3. Test Scrape
print(f"Testing Scraper for URL: {url}")
actor_config = {
    'id': 'junglee~amazon-reviews-scraper',
    'input': {
        "productUrls": [{"url": url}],
        "maxItems": 10, 
        "mode": "hcaptcha",
        "proxyConfiguration": {"useApifyProxy": True}
    }
}

try:
    run_url = f'https://api.apify.com/v2/acts/{actor_config["id"]}/runs?token={APIFY_TOKEN}'
    print("Starting Actor Run...")
    response = requests.post(run_url, json=actor_config['input'], timeout=30)
    print(f"Start Response: {response.status_code}")
    
    if response.status_code != 201:
        print(f"Error Message: {response.text}")
        sys.exit(1)
        
    run_data = response.json()['data']
    run_id = run_data['id']
    print(f"Run Started. ID: {run_id}")
    
    # Poll
    for i in range(10):
        time.sleep(5)
        status_url = f'https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_TOKEN}'
        status_res = requests.get(status_url)
        status = status_res.json()['data']['status']
        print(f"Poll {i+1}: {status}")
        
        if status == 'SUCCEEDED':
            print("Run Succeeded!")
            break
        if status in ['FAILED', 'ABORTED', 'TIMED-OUT']:
            print(f"Run Failed with status: {status}")
            break
            
except Exception as e:
    print(f"Scrape Exception: {e}")
