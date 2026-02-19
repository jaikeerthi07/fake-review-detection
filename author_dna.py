import re
import nltk
from collections import Counter
from textblob import TextBlob

# Ensure necessary NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('taggers/averaged_perceptron_tagger')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    nltk.download('stopwords', quiet=True)

from nltk.corpus import stopwords

class AuthorDNA:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))

    def analyze(self, text):
        if not text or not isinstance(text, str):
            return self._empty_result()

        # Tokenization
        sentences = nltk.sent_tokenize(text)
        words = nltk.word_tokenize(text)
        words_alpha = [w.lower() for w in words if w.isalpha()]
        
        # 1. Average Sentence Length
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        
        # 2. Vocabulary Diversity (TTR)
        unique_words = set(words_alpha)
        vocab_diversity = len(unique_words) / len(words_alpha) if words_alpha else 0
        
        # 3. Stopword Ratio
        stopword_count = sum(1 for w in words_alpha if w in self.stop_words)
        stopword_ratio = stopword_count / len(words_alpha) if words_alpha else 0
        
        # 4. POS Tag Distribution
        pos_tags = nltk.pos_tag(words)
        pos_counts = Counter(tag[:2] for word, tag in pos_tags) # simplify tags (NN, VB, JJ)
        total_pos = len(pos_tags)
        
        noun_ratio = (pos_counts.get('NN', 0) / total_pos) if total_pos else 0
        verb_ratio = (pos_counts.get('VB', 0) / total_pos) if total_pos else 0
        adj_ratio = (pos_counts.get('JJ', 0) / total_pos) if total_pos else 0
        
        # 5. Punctuation Style
        punct_counts = Counter(char for char in text if char in '!?,.')
        total_chars = len(text)
        exclamation_density = (punct_counts.get('!', 0) / total_chars) * 100 if total_chars else 0
        question_density = (punct_counts.get('?', 0) / total_chars) * 100 if total_chars else 0
        
        return {
            'avg_sentence_len': round(avg_sentence_length, 2),
            'vocab_diversity': round(vocab_diversity, 2),
            'stopword_ratio': round(stopword_ratio, 2),
            'pos_ratios': {
                'noun': round(noun_ratio, 2),
                'verb': round(verb_ratio, 2),
                'adj': round(adj_ratio, 2)
            },
            'punctuation': {
                'exclamation_density': round(exclamation_density, 2),
                'question_density': round(question_density, 2)
            },
            'style_label': self._determine_style(avg_sentence_length, vocab_diversity, exclamation_density)
        }

    def _empty_result(self):
         return {
            'avg_sentence_len': 0,
            'vocab_diversity': 0,
            'stopword_ratio': 0,
            'pos_ratios': {'noun': 0, 'verb': 0, 'adj': 0},
            'punctuation': {'exclamation_density': 0, 'question_density': 0},
            'style_label': 'Unknown'
        }

    def _determine_style(self, sent_len, distinct, exclamations):
        """Heuristic style classifier"""
        if exclamations > 1.0:
            return "Expressive / Emotional"
        if sent_len > 20 and distinct > 0.6:
            return "Formal / Complex"
        if sent_len < 10:
            return "Short / Terse"
        if distinct < 0.4:
            return "Repetitive / Simple"
        return "Standard"
