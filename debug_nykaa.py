import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def test_nykaa_scrape():
    url = "https://www.nykaa.com/maybelline-new-york-super-stay-matte-ink-liquid-lipstick/p/231122"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    print(f"Testing URL: {url}")
    try:
        res = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {res.status_code}")
        # print(f"Content Length: {len(res.text)}")
        
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # New Platform Elements logic from app.py
        review_elements = soup.select('div.review-box')
        print(f"Found {len(review_elements)} review elements with 'div.review-box'")
        
        if not review_elements:
             # Fallback check
             review_elements = soup.select('div.t-ZTKy') # Shopsy/Flipkart?
             print(f"Found {len(review_elements)} review elements with 'div.t-ZTKy'")

        reviews = []
        for review in review_elements:
            review_text = ""
            body = review.select_one('div.review-box, p.review-desc')
            if body: review_text = body.get_text().strip()
            
            if review_text:
                reviews.append({'text': review_text})
        
        print(f"Processed {len(reviews)} reviews.")
        
        # Test the fallback logic in app.py
        if not reviews:
            print("No reviews found. Testing synthetic fallback trigger...")
            # This is what app.py should do
            platform = "Nykaa"
            print(f"Platform identified as: {platform}")
            # If reviews is empty, it should return mock reviews.
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_nykaa_scrape()
