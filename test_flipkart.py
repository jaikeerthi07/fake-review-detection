import requests
import time
import json

APIFY_TOKEN = 'YOUR_APIFY_TOKEN_HERE'
ACTOR_ID = 'easyapi~flipkart-product-scraper'
TEST_URL = 'https://www.flipkart.com/samsung-galaxy-m14-5g-smoky-teal-128-gb/p/itm59f77626f2409?pid=MOBGZVGH4XGDGZHP' # Samsung Galaxy M14

def test_flipkart():
    print(f"Testing Flipkart Scraper for {ACTOR_ID}...")
    run_url = f'https://api.apify.com/v2/acts/{ACTOR_ID}/runs?token={APIFY_TOKEN}'
    
    actor_input = {
        "startUrls": [{"url": TEST_URL}],
        "maxReviews": 20,
        "proxyConfiguration": {"useApifyProxy": True}
    }
    
    try:
        response = requests.post(run_url, json=actor_input)
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
                print(f"Run failed with status: {status}")
                # Fetch log
                log_url = f'https://api.apify.com/v2/acts/{ACTOR_ID}/runs/{run_id}/log?token={APIFY_TOKEN}'
                log_res = requests.get(log_url)
                print("Run Log:")
                print(log_res.text[:1000]) # Print first 1000 chars
                return
        
        # Fetch
        items_url = f'https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}&format=json'
        items_res = requests.get(items_url)
        items = items_res.json()
        
        if len(items) > 0:
            print("First item sample:")
            print(json.dumps(items[0], indent=2))
            
            # Save to file
            with open('flipkart_item.json', 'w', encoding='utf-8') as f:
                json.dump(items[0], f, indent=2)
        else:
            print("No items found.")

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_flipkart()
