import requests
import json

BASE_URL = 'http://localhost:5001/api'

def test_scrape_metadata():
    print("\n--- Testing Scraping Metadata ---")
    # Use a known Amazon URL (or Ubuy which redirects)
    url = "https://www.amazon.com/dp/B0D22VRJ63" 
    
    try:
        # Note: Scraping might fail if Amazon blocks requests, but we'll see if we get *any* structure
        response = requests.post(f"{BASE_URL}/scrape", json={'url': url}, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            reviews = data.get('reviews', [])
            if reviews and len(reviews) > 0:
                first_review = reviews[0]
                print(f"First Review Type: {type(first_review)}")
                print(f"First Review Data: {first_review}")
                
                if isinstance(first_review, dict):
                    if 'date' in first_review and 'rating' in first_review:
                         print("✅ SUCCESS: Metadata (date, rating) extraction verified.")
                    else:
                         print("⚠️ WARNING: Dict returned but missing keys.")
                else:
                     print("❌ FAILURE: Reviews returned as strings, not objects.")
            else:
                print("⚠️ No reviews found (might be blocked).")
        else:
            print(f"❌ Scraping Failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_predict_bulk_metadata():
    print("\n--- Testing Predict Bulk Metadata Preservation ---")
    # Simulate structured input
    payload = {
        'reviews': [
            {'text': 'Great product!', 'date': 'January 1, 2024', 'rating': 5.0},
            {'text': 'Terrible.', 'date': 'February 1, 2024', 'rating': 1.0}
        ]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/predict_bulk", json=payload)
        if response.status_code == 200:
            results = response.json().get('results', [])
            if results:
                first = results[0]
                print(f"Result Keys: {first.keys()}")
                if 'date' in first and 'rating' in first and 'trust_score' in first:
                    print(f"✅ SUCCESS: Metadata preserved in prediction results.")
                    print(f"Sample Trust Score: {first['trust_score']}")
                else:
                    print("❌ FAILURE: Metadata lost in prediction.")
            else:
                print("❌ No results returned.")
        else:
             print(f"❌ Prediction Failed: {response.status_code}")
             
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_scrape_metadata()
    test_predict_bulk_metadata()
