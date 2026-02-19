import re
from textblob import TextBlob
import nltk
from collections import Counter

# Ensure dependencies are downloaded (can be moved to startup script)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

class LieDetector:
    def __init__(self):
        self.exaggeration_words = {
            'amazing', 'awesome', 'best', 'worst', 'incredible', 'perfect', 
            'terrible', 'horrible', 'excellent', 'outstanding', 'fantastic',
            'superb', 'sublime', 'magnificent', 'unbelievable', 'absolute',
            'extremely', 'totally', 'completely', 'utterly'
        }
        
        self.deceptive_patterns = [
            r'\b(trust me)\b',
            r'\b(believe me)\b',
            r'\b(honestly)\b',
            r'\b(to be honest)\b',
            r'\b(truth be told)\b',
            r'\b(i swear)\b',
            r'\b(literally)\b'
        ]
        
        self.promotional_patterns = [
            r'\b(check out)\b',
            r'\b(click here)\b',
            r'\b(link in bio)\b',
            r'\b(buy now)\b',
            r'\b(discount)\b',
            r'\b(coupon)\b',
            r'\b(use code)\b',
            r'\b(visit my)\b',
            r'\b(subscribe)\b'
        ]

    def analyze(self, text):
        if not text:
            return self._empty_result()
            
        blob = TextBlob(text)
        
        return {
            'deception_score': self._detect_deceptive_patterns(text),
            'exaggeration_score': self._score_exaggeration(text),
            'emotional_intensity': self._emotional_intensity(blob),
            'repetition_score': self._detect_repetition(text),
            'promotional_score': self._detect_promotional(text),
            'details': {
                'subjectivity': float(blob.sentiment.subjectivity),
                'word_count': len(text.split())
            }
        }

    def _empty_result(self):
        return {
            'deception_score': 0,
            'exaggeration_score': 0,
            'emotional_intensity': 0,
            'repetition_score': 0,
            'promotional_score': 0,
            'details': {}
        }

    def _detect_deceptive_patterns(self, text):
        """
        Detects common linguistic cues of deception:
        - "Trust me", "Honestly" (Subconscious need to verify truth)
        - Lack of self-reference (Distancing language - though less reliable in reviews)
        """
        text_lower = text.lower()
        score = 0
        
        # Check for specific phrases
        for pattern in self.deceptive_patterns:
            if re.search(pattern, text_lower):
                score += 20 # High penalty for "Trust me" etc.
                
        # Cap at 100
        return min(score, 100)

    def _score_exaggeration(self, text):
        """
        Counts superlatives and intensifiers.
        Fake reviews often use more "extreme" language.
        """
        words = re.findall(r'\w+', text.lower())
        count = sum(1 for w in words if w in self.exaggeration_words)
        
        # Calculate density: matches per 100 words
        if not words: return 0
        density = (count / len(words)) * 100
        
        # Scale: > 5% exaggeration is high
        score = min(density * 10, 100) 
        return round(score, 2)

    def _emotional_intensity(self, blob):
        """
        Combination of polarity magnitude (how positive/negative) 
        and subjectivity (how opinionated).
        Fake reviews often have very high subjectivity and extreme polarity.
        """
        polarity = abs(blob.sentiment.polarity) # 0 to 1
        subjectivity = blob.sentiment.subjectivity # 0 to 1
        
        # Intensity = (Polarity + Subjectivity) / 2 * 100
        intensity = ((polarity + subjectivity) / 2) * 100
        return round(intensity, 2)

    def _detect_repetition(self, text):
        """
        Detects repetitive n-grams or words.
        Fake reviews might be copy-pasted or generated with repetitive loops.
        """
        words = re.findall(r'\w+', text.lower())
        if len(words) < 10: return 0
        
        # Check for unigram repetition (excessive use of same words)
        word_counts = Counter(words)
        most_common = word_counts.most_common(3)
        
        repetition_penalty = 0
        for word, count in most_common:
            # Common stop words shouldn't trigger this too hard, but high freq of content words is suspicious
            if word not in ['the', 'and', 'a', 'to', 'of', 'it', 'is', 'i', 'in']:
                if count > len(words) * 0.2: # If a word makes up > 20% of the text
                    repetition_penalty += 30
                    
        return min(repetition_penalty, 100)

    def _detect_promotional(self, text):
        """
        Detects marketing speak.
        """
        text_lower = text.lower()
        score = 0
        
        for pattern in self.promotional_patterns:
            if re.search(pattern, text_lower):
                score += 50 
                
        return min(score, 100)
