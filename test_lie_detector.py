from lie_detector import LieDetector

def test_lie_detector():
    ld = LieDetector()
    
    # Test Case 1: Exaggerated Fake Review
    fake_text = "This is the absolute best amazing product ever!!! Trust me, it is incredible."
    res1 = ld.analyze(fake_text)
    print("\n--- Test 1: Fake/Exaggerated ---")
    print(f"Text: {fake_text}")
    print(res1)
    
    # Test Case 2: Normal Real Review
    real_text = "It works as expected. The battery life is okay but could be better."
    res2 = ld.analyze(real_text)
    print("\n--- Test 2: Normal/Real ---")
    print(f"Text: {real_text}")
    print(res2)
    
    # Test Case 3: Promotional
    promo_text = "Check out my profile for a discount code! Buy now for 50% off."
    res3 = ld.analyze(promo_text)
    print("\n--- Test 3: Promotional ---")
    print(f"Text: {promo_text}")
    print(res3)

if __name__ == "__main__":
    test_lie_detector()
