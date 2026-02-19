import requests
import json

APIFY_TOKEN = 'YOUR_APIFY_TOKEN_HERE'
RUN_ID = 'IwgsCMu2hE5Fz6Oa2'

def get_dataset_items():
    # 1. Get Run to find defaultDatasetId
    run_url = f'https://api.apify.com/v2/actor-runs/{RUN_ID}?token={APIFY_TOKEN}'
    run_res = requests.get(run_url)
    if run_res.status_code != 200:
        print(f"Failed to get run: {run_res.status_code}")
        return

    dataset_id = run_res.json()['data']['defaultDatasetId']
    print(f"Dataset ID: {dataset_id}")
    
    # 2. Fetch Items
    items_url = f'https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}'
    items_res = requests.get(items_url)
    if items_res.status_code == 200:
        items = items_res.json()
        print(f"Fetched {len(items)} items.")
        if items:
            print(json.dumps(items[0], indent=2))
            # Check for reviews
            if 'reviews' in items[0]:
                 print(f"Review count in first item: {len(items[0]['reviews'])}")
    else:
        print(f"Failed to fetch items: {items_res.status_code}")

if __name__ == '__main__':
    get_dataset_items()
