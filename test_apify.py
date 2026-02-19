import requests
import time
import json

APIFY_TOKEN = 'YOUR_APIFY_TOKEN_HERE'
ACTOR_ID = 'junglee~amazon-reviews-scraper'
TEST_URL = 'https://www.amazon.com/Apple-iPhone-12-64GB-Blue/dp/B08N5KWB9H' # Amazon.com US URL

def test_scrape():
    print(f"Testing Apify Scraper for {ACTOR_ID} with {TEST_URL}...")
    run_url = f'https://api.apify.com/v2/acts/{ACTOR_ID}/runs?token={APIFY_TOKEN}'
    
    actor_input = {
        "productUrls": [{"url": TEST_URL}],
        "maxItems": 5,
        "mode": "hcaptcha",
        "proxyConfiguration": {"useApifyProxy": True}
    }
    
    print("Sending request to start actor...")
    try:
        response = requests.post(run_url, json=actor_input)
        print(f"Start Status: {response.status_code}")
        if response.status_code != 201:
            print(f"Error starting actor: {response.text}")
            return

        run_data = response.json()['data']
        run_id = run_data['id']
        dataset_id = run_data['defaultDatasetId']
        print(f"Run ID: {run_id}")
        
        # Poll
        for i in range(20):
            time.sleep(3)
            status_url = f'https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_TOKEN}'
            status_res = requests.get(status_url)
            status = status_res.json()['data']['status']
            print(f"Poll {i+1}: {status}")
            
            if status == 'SUCCEEDED':
                break
            if status in ['FAILED', 'ABORTED', 'TIMED-OUT']:
                print("Run failed.")
                return
        else:
            print("Timed out.")
            return

        # Fetch
        print("Fetching items...")
        items_url = f'https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}&format=json'
        items_res = requests.get(items_url)
        items = items_res.json()
        if len(items) > 0:
            print("Saving first item to scraped_item.json")
            with open('scraped_item.json', 'w', encoding='utf-8') as f:
                json.dump(items[0], f, indent=2)

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_scrape()
