import requests
import time

APIFY_TOKEN = 'YOUR_APIFY_TOKEN_HERE'
TEST_URL = 'https://www.flipkart.com/samsung-galaxy-m14-5g-smoky-teal-128-gb/p/itm59f77626f2409'

ACTORS = [
    'codingfrontend~flipkart-reviews-scraper',
    'natanielsantos~flipkart-reviews-scraper',
    'getdataforme~flipkart-reviews-scraper'
]

def test_actor(actor_id):
    print(f"Testing {actor_id}...")
    run_url = f'https://api.apify.com/v2/acts/{actor_id}/runs?token={APIFY_TOKEN}'
    
    actor_input = {
        "startUrls": [{"url": TEST_URL}],
        "maxItems": 5,
        "proxyConfiguration": {"useApifyProxy": True}
    }
    
    response = requests.post(run_url, json=actor_input)
    if response.status_code == 201:
        print(f"SUCCESS: {actor_id} started.")
        run_data = response.json()['data']
        print(f"Run ID: {run_data['id']}")
        return True
    else:
        print(f"FAILED: {actor_id} - {response.status_code}")
        try:
            print(response.json().get('error', {}).get('message'))
        except:
            print(response.text)
        return False

for actor in ACTORS:
    if test_actor(actor):
        break
