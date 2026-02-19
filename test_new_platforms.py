import requests
import json

APIFY_TOKEN = 'YOUR_APIFY_TOKEN_HERE'

# Helper function to run actor and check result
def test_actor(name, actor_id, input_data):
    print(f"\n--- Testing {name} ({actor_id}) ---")
    run_url = f'https://api.apify.com/v2/acts/{actor_id}/runs?token={APIFY_TOKEN}'
    
    try:
        response = requests.post(run_url, json=input_data)
        if response.status_code == 201:
            run_data = response.json()['data']
            print(f"STARTED: Run ID {run_data['id']}")
            return run_data['id']
        else:
            print(f"FAILED to start: {response.status_code}")
            try:
                print(response.json().get('error', {}).get('message'))
            except:
                print(response.text)
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

# 1. Myntra Reviews (trying a likely ID based on search)
# Search said "Myntra Reviews Scraper" exists. 
# Common format: username/actor-name. "dashblock" is a common dev for these, or "canh" etc. 
# I will try a few likely IDs if exact one isn't known, or use the one found in search if specific username was given.
# Search result [1] linked to 'apify.com/...' but didn't warn of specific username.
# I will try 'blazing-scraper/myntra-reviews-scraper' or similar if I can guess, 
# but let's try a search via API first or just guessing 'curious_coder/myntra-reviews-scraper' (example) is hard.
# BETTER STRATEGY: Use a known working one like eBay which has official-ish support.

# eBay is often 'drobnikj/ebay-scraper' or similar.
# Let's try 'maxcopell/ebay-reviews-scraper' or just 'epctex/ebay-review-scraper'

# Actually, let's try the generic "canh/myntra-reviews" or similar if we can find it.
# Since I can't browse the store interactively, I will test 'drobnikj/ebay-reviews-scraper' (if exists) or 'epctex/ebay-scraper'.
# Search result [1] for eBay mentioned "eBay Reviews Scraper".
# Let's try 'smart-scraper/ebay-reviews-scraper'

ACTORS_TO_TEST = [
    {
        'name': 'Myntra Reviews',
        'id': 'lhotse~myntra-reviews-scraper', # Guessing based on common successful scrapers or search
        'input': {
            "startUrls": [{"url": "https://www.myntra.com/tshirts/hrx-by-hrithik-roshan/hrx-by-hrithik-roshan-men-yellow-printed-cotton-pure-cotton-t-shirt/1700944/buy"}], 
            "maxItems": 5,
            "proxyConfiguration": {"useApifyProxy": True}
        }
    },
    {
        'name': 'eBay Reviews',
        'id': 'drobnikj~ebay-reviews-scraper', 
        'input': {
            "startUrls": [{"url": "https://www.ebay.com/itm/123456789"}], # Need valid URL
            "maxReviews": 5,
            "proxyConfiguration": {"useApifyProxy": True}
        }
    }
]

# Note: Without exact IDs, this is hit/miss. 
# I will try to use the `YOUR_APIFY_TOKEN_HERE` to list available actors if possible? No.

# Let's try to search specifically for the actor ID using python first?
# No, let's try a direct run of the most likely free one: "epctex/ebay-scraper" is usually reliable.
# But user wants REVIEWS.
# "trudax/ebay-reviews-scraper"

# Let's just try to scrape 'Snapdeal' via generic HTML extraction?
# It might be easier than guessing actor IDs.
# But the user asked for "other... scraper", implying integration.

# Let's try to implement a CUSTOM beautifulsoup scraper for Snapdeal.
# It's less likely to block than Amazon/Flipkart.
pass
