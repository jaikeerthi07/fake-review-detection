import requests
from bs4 import BeautifulSoup

url = "https://www.ubuy.co.in/product/R1K5YEMBM-hand-warmers-rechargerable-2-pack-4000mah-electric-handwarmers-reusable-portable-pocket-heater-gifts-for-women-men"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


try:
    s = requests.Session()
    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })
    print(f"Fetching {url}...")
    res = s.get(url, timeout=15)
    print(f"Status: {res.status_code}")
    
    soup = BeautifulSoup(res.text, 'html.parser')

    soup = BeautifulSoup(res.text, 'html.parser')

    # Extract JS variables
    import re
    import json
    import urllib.parse
    import base64

    script_content = ""
    for script in soup.find_all('script'):
        if script.string and "var review_url" in script.string:
            script_content = script.string
            break
    
    if not script_content:
        print("Could not find script with review_url")
        exit()

    def get_var(name):
        match = re.search(r"var " + name + r"\s*=\s*['\"]([^'\"]+)['\"];", script_content)
        if match: return match.group(1)
        return ""

    review_url = get_var("review_url")
    selected_asin = get_var("selected_asin")
    parent_asin = get_var("parent_asin")
    product_id = get_var("product_id")
    product_name = get_var("product_name")
    lang = get_var("lang")
    storename = get_var("storename")
    substorename = get_var("substorename")
    entity_id = get_var("entity_id")
    csrftoken_common = get_var("csrftoken_common")
    
    print(f"Extracted: ID={product_id}, ASIN={selected_asin}, Token={csrftoken_common[:10]}...")

    params = {
        "sa": selected_asin,
        "pa": parent_asin,
        "pi": product_id,
        "pnm": product_name,
        "rp": 1,
        "lng": lang,
        "rsb": 0,
        "rst": "",
        "d": "d",
        "sname": storename,
        "sbname": substorename,
        "token": csrftoken_common,
        "entity_id": entity_id,
        "customer_id": "",
        "website_id": "19", # Hardcoded in JS
        "s_id": "31" # Hardcoded/Variable in JS
    }
    
    # Simulate JS: btoa(unescape(encodeURIComponent(JSON.stringify(review_query_params))))
    # Python: base64.b64encode(urllib.parse.quote(json.dumps(params)).encode('utf-8')).decode('utf-8')
    # Wait, JS encodeURIComponent encodes everything. Python quote might be slightly different suitable for verify.
    # Let's try standard flow.
    
    json_str = json.dumps(params, separators=(',', ':')) # JS stringify usually no spaces
    encoded_str = urllib.parse.quote(json_str)
    # JS btoa takes a string.
    payload = base64.b64encode(encoded_str.encode('utf-8')).decode('utf-8')
    
    print(f"Payload: {payload[:20]}...")
    
    review_full_url = f"{review_url}?p={payload}&is_one_search="
    print(f"Fetching reviews from: {review_full_url}")
    
    # Update headers for AJAX
    s.headers.update({
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': url,
        'Accept': 'text/html, */*; q=0.01'
    })
    
    review_res = s.get(review_full_url)
    print(f"Review Status: {review_res.status_code}")
    
    with open('d:\\fake review detection\\ubuy_reviews.html', 'w', encoding='utf-8') as f:
        f.write(review_res.text)
        
    print("Saved reviews to d:\\fake review detection\\ubuy_reviews.html")

except Exception as e:
    print(f"Error: {e}")
