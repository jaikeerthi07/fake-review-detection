import requests
import json
if __name__ == '__main__':
    url = 'http://localhost:5001/api/scrape'
    print("Testing Flipkart Scraper locally via API:")
    try:
        response = requests.post(url, json={'url': 'https://www.flipkart.com/samsung-galaxy-m14-5g/p/itm2a666kH'}, timeout=10)
        if response.status_code == 200:
            reviews = response.json().get('reviews', [])
            print(f"Scraped {len(reviews)} reviews. Now analyzing...")
            
            predict_url = 'http://localhost:5001/api/predict_bulk'
            pred_response = requests.post(predict_url, json={'reviews': reviews}, timeout=30)
            print(f"Analysis Status Code: {pred_response.status_code}")
            
            if pred_response.status_code == 200:
                results = pred_response.json().get('results', [])
                with open('test_analysis_results.json', 'w') as f:
                    json.dump(pred_response.json(), f, indent=2)
                
                print("\nSample Predictions:")
                for r in results[:5]:
                    print(f"- Text: {r['text'][:50]}...")
                    print(f"  Label: {r['label']} (Trust: {r['trust_score']}%)")
            else:
                print(f"Analysis failed: {pred_response.text}")
        
    except Exception as e:
        print(f"Failed: {e}")
