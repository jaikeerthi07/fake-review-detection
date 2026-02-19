
import requests
import json
import logging
import sys

# Setup logger to output to stdout properly
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

APIFY_TOKEN = 'YOUR_APIFY_TOKEN_HERE'
DATASET_ID = 'cmzDyHv2ANVmzwj3r'

def fetch_dataset():
    print(f"Fetching items from Dataset: {DATASET_ID}...")
    items_url = f'https://api.apify.com/v2/datasets/{DATASET_ID}/items?token={APIFY_TOKEN}&format=json'
    
    try:
        response = requests.get(items_url)
        if response.status_code != 200:
            print(f"Error fetching dataset: {response.text}")
            return

        items = response.json()
        print(f"Items found: {len(items)}")
        
        if len(items) > 0:
            # Write first item to a file for inspection
            with open('debug_output.json', 'w', encoding='utf-8') as f:
                json.dump(items[0], f, indent=2)
            print("First item written to debug_output.json")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    fetch_dataset()
