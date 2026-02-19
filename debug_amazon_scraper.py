import requests
from bs4 import BeautifulSoup

url = "https://www.amazon.in/WOOYNEX-Magazines-Entryway-Antic-Burning/dp/B0D22VRJ63"
print(f"Scraping URL: {url}")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

try:
    res = requests.get(url, headers=headers, timeout=10)
    print(f"Status Code: {res.status_code}")
    
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # Check for Amazon's captcha
    if "Type the characters you see in this image" in res.text:
        print("Blocked by Amazon CAPTCHA")
    
    review_elements = soup.select('div[data-hook="review"]')
    print(f"Found {len(review_elements)} review elements via selector 'div[data-hook=\"review\"]'")
    
    # Check if there are any reviews at all
    reviews_count_text = soup.select_one('#acrCustomerReviewText')
    if reviews_count_text:
        print(f"Page says: {reviews_count_text.text.strip()}")
    else:
        print("Could not find review count on page.")

    # Save HTML for inspection
    with open("amazon_debug.html", "w", encoding="utf-8") as f:
        f.write(soup.prettify())
    print("Saved HTML to amazon_debug.html")

    for i, review in enumerate(review_elements[:3]):
        body = review.select_one('span[data-hook="review-body"]')
        if body:
            print(f"Review {i+1}: {body.get_text().strip()[:50]}...")
        else:
            print(f"Review {i+1}: Body not found")

except Exception as e:
    print(f"Error: {e}")
