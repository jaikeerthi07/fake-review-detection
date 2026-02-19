import requests
from bs4 import BeautifulSoup
import json

def get_shopclues_reviews():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print("Fetching ShopClues category...")
    try:
        cat_url = "https://www.shopclues.com/mens-t-shirts.html"
        cat_response = requests.get(cat_url, headers=headers)
        
        soup = BeautifulSoup(cat_response.content, 'html.parser')
        
        product_link = None
        # ShopClues links: https://www.shopclues.com/product-name.html
        # Look for links inside category listing
        for a in soup.find_all('a', href=True):
            if '.html' in a['href'] and 'www.shopclues.com' in a['href'] and '/mens-t-shirts.html' not in a['href']:
                product_link = a['href']
                break
        
        if not product_link:
            print("No product link found.")
            # Fallback manual URL if needed
            return

        print(f"Testing URL: {product_link}")
        
        # Fetch Product Page
        prod_response = requests.get(product_link, headers=headers)
        prod_soup = BeautifulSoup(prod_response.content, 'html.parser')
        
        # Reviews are usually in #review-data or similar
        reviews = []
        # Review container inspection needed. 
        # Guessing logic based on typical structure.
        # Often div class="review_desc"
        
        for review_div in prod_soup.find_all('div', {'class': 'review_desc'}):
             text = review_div.text.strip()
             reviews.append({'text': text, 'source': 'ShopClues'})
             
        # Alternative: Try to find "Review" tab?
        
        print(f"Found {len(reviews)} reviews.")
        print(json.dumps(reviews[:2], indent=2))

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    get_shopclues_reviews()
