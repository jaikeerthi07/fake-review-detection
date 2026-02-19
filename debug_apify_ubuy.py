import requests
import time
import json
import sys

APIFY_TOKEN = 'YOUR_APIFY_TOKEN_HERE'
url = "https://www.ubuy.co.in/product/R1K5YEMBM-hand-warmers-rechargerable-2-pack-4000mah-electric-handwarmers-reusable-portable-pocket-heater-gifts-for-women-men"

# Actor: apify/puppeteer-scraper
actor_id = "apify~puppeteer-scraper"

input_data = {
    "startUrls": [{"url": url}],
    "pageFunction": """async function pageFunction(context) {
        const { page, request, log } = context;
        log.info(`Processing ${request.url}`);
        
        // Scroll to bottom to trigger lazy loading
        await page.evaluate(async () => {
            await new Promise((resolve, reject) => {
                var totalHeight = 0;
                var distance = 200;
                var timer = setInterval(() => {
                    var scrollHeight = document.body.scrollHeight;
                    window.scrollBy(0, distance);
                    totalHeight += distance;
                    if(totalHeight >= scrollHeight){
                        clearInterval(timer);
                        resolve();
                    }
                }, 100);
            });
        });

        // Wait for reviews container
        try {
            await page.waitForSelector('#product-reviews', { timeout: 15000 });
            // Wait a bit more for content to populate
            await page.waitForTimeout(3000);
        } catch(e) { log.info("No #product-reviews found"); }

        // Dump everything
        const html = await page.content();
        return { html };
    }""",
    "proxyConfiguration": { "useApifyProxy": True },
}

try:
    print(f"Starting Actor {actor_id}...")
    run_url = f'https://api.apify.com/v2/acts/{actor_id}/runs?token={APIFY_TOKEN}'
    response = requests.post(run_url, json=input_data, timeout=30)
    
    if response.status_code != 201:
        print(f"Error Message: {response.text}")
        sys.exit(1)
        
    run_data = response.json()['data']
    run_id = run_data['id']
    print(f"Run Started. ID: {run_id}")
    
    # Poll
    dataset_id = run_data['defaultDatasetId']
    
    for i in range(20):
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
            
    # Fetch Results
    if status == 'SUCCEEDED':
        items_url = f'https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}'
        items_res = requests.get(items_url)
        items = items_res.json()
        if items:
            html = items[0].get('html')
            with open('d:\\fake review detection\\ubuy_rendered.html', 'w', encoding='utf-8') as f:
                f.write(html)
            print("Saved rendered HTML to d:\\fake review detection\\ubuy_rendered.html")
        else:
            print("No items returned.")

except Exception as e:
    print(f"Exception: {e}")
