import requests

APIFY_TOKEN = 'YOUR_APIFY_TOKEN_HERE'
ACTOR_ID = 'easyapi~flipkart-product-scraper'
TEST_URL = 'https://www.flipkart.com/samsung-galaxy-m14-5g-smoky-teal-128-gb/p/itm59f77626f2409?pid=MOBGZVGH4XGDGZHP'

def test_actor():
    print(f"Testing {ACTOR_ID}...")
    run_url = f'https://api.apify.com/v2/acts/{ACTOR_ID}/runs?token={APIFY_TOKEN}'
    
    actor_input = {
        "startUrls": [{"url": TEST_URL}],
        "maxItems": 5,
        "proxyConfiguration": {"useApifyProxy": True}
    }
    
    response = requests.post(run_url, json=actor_input)
    if response.status_code != 201:
        print(f"FAILED: {response.status_code}")
        try:
            print(response.json())
        except:
            print(response.text)
    else:
        print("SUCCESS")
        print(response.json())

if __name__ == '__main__':
    test_actor()
