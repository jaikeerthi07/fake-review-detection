import requests
from bs4 import BeautifulSoup
import re
import json

def get_tatacliq_reviews():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/plain, */*'
    }
    
    print("Fetching TataCliq category...")
    try:
        cat_url = "https://www.tatacliq.com/men-t-shirts/c-msh1100-300" # Found on site structure
        cat_response = requests.get(cat_url, headers=headers)
        
        # TataCliq is heavily React/Next.js. Need to find JSON or links.
        # Often embedded in <script id="__NEXT_DATA__"> or similar
        soup = BeautifulSoup(cat_response.content, 'html.parser')
        
        product_id = None
        # Try to find a link with /p-mp...
        for a in soup.find_all('a', href=True):
            if '/p-mp' in a['href']:
                # extracting ID: /p-mp000000012345
                match = re.search(r'mp(\d+)', a['href'])
                if match:
                    product_id = "mp" + match.group(1)
                    print(f"Found Product ID: {product_id} from {a['href']}")
                    break
        
        if not product_id:
            # Fallback hardcoded ID test if scrape fails (just to check API)
            print("Could not find product link. Trying hardcoded ID mp000000018596078 (Example)")
            product_id = "mp000000018596078"

        # 2. Fetch Reviews API
        # API pattern varies. Common: 
        # https://ises-ind.tatacliq.com/marketplaceweb/v1/ratingreview/product-rating-review/mp000000018596078?isReviewRequired=true
        review_url = f"https://ises-ind.tatacliq.com/marketplaceweb/v1/ratingreview/product-rating-review/{product_id}?isReviewRequired=true"
        print(f"Fetching reviews from {review_url}")
        
        review_response = requests.get(review_url, headers=headers)
        if review_response.status_code == 200:
            data = review_response.json()
            reviews = data.get('reviews', []) # Check structure
            print(json.dumps(data, indent=2)) 
        else:
            print(f"Failed to fetch reviews: {review_response.status_code}")
            print(review_response.text[:200])

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    get_tatacliq_reviews()
