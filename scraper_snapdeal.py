import requests
from bs4 import BeautifulSoup
import json

def scrape_snapdeal(url):
    print(f"Scraping Snapdeal: {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch page: {response.status_code}")
            return []
            
        soup = BeautifulSoup(response.content, 'html.parser')
        reviews = []
        
        # Snapdeal review structure (needs verification, based on typical layout)
        # Often in <div class="user-review">
        review_blocks = soup.find_all('div', {'class': 'user-review'})
        
        for block in review_blocks:
            try:
                # Username
                author_elem = block.find('div', {'class': '_reviewUserName'})
                author = author_elem.get('title') if author_elem else "Anonymous"
                
                # Rating
                rating_elem = block.find('div', {'class': 'rating-stars'})
                rating = len(rating_elem.find_all('i', {'class': 'active'})) if rating_elem else 0
                
                # Title
                title_elem = block.find('div', {'class': 'head'})
                title = title_elem.text.strip() if title_elem else ""
                
                # Text
                text_elem = block.find('p')
                text = text_elem.text.strip() if text_elem else ""
                
                # Date
                date_elem = block.find('div', {'class': 'date'})
                date = date_elem.text.strip() if date_elem else ""
                
                if text:
                    reviews.append({
                        'author': author,
                        'rating': rating,
                        'title': title,
                        'text': text,
                        'date': date,
                        'source': 'Snapdeal'
                    })
            except Exception as e:
                print(f"Error parsing review block: {e}")
                continue
                
        print(f"Found {len(reviews)} reviews.")
        return reviews

    except Exception as e:
        print(f"Scraper error: {e}")
        return []

if __name__ == '__main__':
    # Dynamically find a product URL to test
    try:
        print("Fetching Snapdeal category page to find a product...")
        home_response = requests.get("https://www.snapdeal.com/products/men-apparel-tshirts", headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        home_soup = BeautifulSoup(home_response.content, 'html.parser')
        
        # Find any product link (usually /product/...)
        product_link = None
        # Snapdeal product links often look like: https://www.snapdeal.com/product/name/id
        # In category page, they might be in <a class="dp-widget-link" href="...">
        for a in home_soup.find_all('a', href=True):
            if '/product/' in a['href']:
                product_link = a['href']
                break
        
        if product_link:
            test_url = product_link if product_link.startswith('http') else f"https://www.snapdeal.com{product_link}"
            print(f"Found test URL: {test_url}")
            reviews = scrape_snapdeal(test_url)
            print(json.dumps(reviews, indent=2))
        else:
            print("Could not find a product URL on the homepage.")
            
    except Exception as e:
        print(f"Error finding test URL: {e}")
