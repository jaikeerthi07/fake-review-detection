import requests
import json

BASE_URL = "http://localhost:5001"

TEST_URLS = [
    {"name": "Amazon", "url": "https://www.amazon.in/dp/B08L5VJYV7"},
    {"name": "Flipkart", "url": "https://www.flipkart.com/apple-iphone-12-blue-64-gb/p/itm577ef37c1524d"},
    {"name": "Myntra", "url": "https://www.myntra.com/tshirts/hrx-by-hrithik-roshan/hrx-by-hrithik-roshan-men-yellow-printed-cotton-pure-cotton-t-shirt/1700944/buy"},
    {"name": "Meesho", "url": "https://www.meesho.com/p/6p3s0z"},
    {"name": "Ajio", "url": "https://www.ajio.com/men-t-shirts/c/830216001"},
    {"name": "Nykaa", "url": "https://www.nykaa.com/l-oreal-paris-revitalift-hyaluronic-acid-serum/p/865422"}
]

def verify_platforms():
    print(f"Starting verification against {BASE_URL}...")
    
    for test in TEST_URLS:
        print(f"\nTesting {test['name']}...")
        try:
            response = requests.post(f"{BASE_URL}/api/scrape", json={"url": test['url']}, timeout=30)
            if response.status_code == 200:
                data = response.json()
                reviews = data.get('reviews', [])
                count = data.get('count', 0)
                print(f"SUCCESS: Found {count} reviews.")
                if reviews:
                    print(f"Sample source: {reviews[0].get('source')}")
            else:
                print(f"FAILED: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    verify_platforms()
