import json
from app import app

client = app.test_client()

urls = [
    "https://www.myntra.com/some-url",
    "https://www.meesho.com/some-url",
    "https://www.ajio.com/some-url",
    "https://www.bigbasket.com/some-url",
    "https://www.nykaa.com/some-url",
    "https://www.shopsy.in/some-url",
]

results = {}
for url in urls:
    response = client.post('/api/scrape', json={'url': url})
    if response.status_code == 200:
        data = json.loads(response.data)
        reviews = data.get('reviews', [])
        platforms = list(set(r.get('source', '') for r in reviews))
        ratings = [r.get('rating') for r in reviews if r.get('rating')]
        
        results[url] = {
            "status": "Success",
            "platforms": platforms,
            "ratings": ratings,
            "count": len(reviews)
        }
    else:
        results[url] = {
            "status": "Failed",
            "error_data": response.data.decode('utf-8')
        }

with open("test_platforms_api_results.json", "w") as f:
    json.dump(results, f, indent=4)
