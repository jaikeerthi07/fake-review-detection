import requests
from bs4 import BeautifulSoup
import re
import json

def get_myntra_reviews():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json'
    }
    
    # 1. Get a product ID from the category page
    print("Fetching Myntra category page...")
    try:
        cat_response = requests.get("https://www.myntra.com/men-tshirts", headers=headers)
        if cat_response.status_code != 200:
            print(f"Failed to fetch category: {cat_response.status_code}")
            return

        # Myntra embeds data in script tags usually, or simple hrefs.
        # Let's look for hrefs like */buy
        soup = BeautifulSoup(cat_response.content, 'html.parser')
        product_link = None
        for a in soup.find_all('a', href=True):
            if '/buy' in a['href']:
                product_link = a['href']
                break
        
        if not product_link:
            print("No product link found.")
            return

        # Extract ID
        # Link: /tshirts/brand/product/12345/buy
        match = re.search(r'/(\d+)/buy', product_link)
        if not match:
             print(f"Could not extract ID from {product_link}")
             return
             
        product_id = match.group(1)
        print(f"Found Product ID: {product_id}")
        
        # 2. Fetch Reviews API
        # URL pattern for reviews: https://www.myntra.com/gateway/v2/product/{id}/reviews
        review_url = f"https://www.myntra.com/gateway/v2/product/{product_id}/reviews"
        print(f"Fetching reviews from {review_url}")
        
        review_response = requests.get(review_url, headers=headers)
        if review_response.status_code == 200:
            data = review_response.json()
            reviews = data.get('reviews', [])
            print(f"Successfully fetched {len(reviews)} reviews.")
            print(json.dumps(reviews[:2], indent=2)) # Print first 2
        else:
            print(f"Failed to fetch reviews: {review_response.status_code}")
            print(review_response.text[:200])
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    get_myntra_reviews()
