from author_dna import AuthorDNA

def test_author_dna():
    dna = AuthorDNA()
    
    # Test 1: Simple/Repetitive (Bot-like)
    simple_text = "The product is good. I like it. It works well. The price is good."
    res1 = dna.analyze(simple_text)
    print("\n--- Test 1: Simple/Repetitive ---")
    print(f"Text: {simple_text}")
    print(res1)
    
    # Test 2: Formal/Complex
    formal_text = "Upon thorough examination, the device demonstrates exceptional build quality, although the battery performance leaves something to be desired in extended use scenarios."
    res2 = dna.analyze(formal_text)
    print("\n--- Test 2: Formal/Complex ---")
    print(f"Text: {formal_text}")
    print(res2)
    
    # Test 3: Expressive/Emotional
    emotional_text = "OMG!!! I absolutely LOVE this product! It's the best thing ever?! Seriously, buy it now!!!"
    res3 = dna.analyze(emotional_text)
    print("\n--- Test 3: Expressive/Emotional ---")
    print(f"Text: {emotional_text}")
    print(res3)

if __name__ == "__main__":
    test_author_dna()
