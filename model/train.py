import pandas as pd
import numpy as np
import pickle
import os
import re
import json
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from textblob import TextBlob

# Function to engineer features (Sentiment Polarity)
# Note: For simplicity in this demo, we'll stick to a robust TF-IDF + SVM pipeline first.
# Adding custom features like polarity often requires a custom transformer class which can get complex 
# to serialize with pickle if the class definition isn't shared. 
# We'll stick to a pure sklearn pipeline for robustness, but use N-grams which SVM loves.

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return text

def generate_dummy_data(n_samples=2000):
    """Generates a larger synthetic dataset."""
    fake_reviews = [
        "This product is amazing! I use it every day.",
        "Worst purchase ever. Do not buy this.",
        "Absolutely fantastic quality, highly recommended.",
        "It broke after one use. Terrible.",
        "I received a box of rocks instead of the phone.",
        "Five stars! Best service ever.",
        "Scam! They took my money and never delivered.",
        "Okay product, but a bit expensive.",
        "Great value for money.",
        "Total waste of time and money.",
        "I love this brand, they never disappoint.",
        "The item arrived damaged and the support was rude."
    ]
    
    data = []
    labels = []
    for _ in range(n_samples):
        is_fake = np.random.choice([0, 1])
        base_review = np.random.choice(fake_reviews)
        
        if is_fake:
            # Fake: Extremes, generic, repetitive
            review = base_review + " " + np.random.choice(["Highly recommend!", "Don't buy!", "Best ever!", "Scam!", "Wow!", "!!"])
        else:
            # Genuine: More moderate, specific details (simulated)
            review = base_review + " " + "I noticed the packaging was slightly dented but the product works fine. Validated purchase."
        
        data.append(review)
        labels.append(is_fake)
        
    return pd.DataFrame({'text': data, 'label': labels})

def train_model():
    print("Generating synthetic data (Pro Version)...")
    df = generate_dummy_data(2000)
    
    df['clean_text'] = df['text'].apply(clean_text)
    
    X = df['clean_text']
    y = df['label']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training Enhanced SVM Model...")
    
    # Pipeline: TF-IDF (1-3 ngrams) -> LinearSVC (wrapped in CalibratedClassifierCV for probabilities)
    # LinearSVC is faster and often better for text than Naive Bayes.
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 3), max_features=10000)),
        ('clf', CalibratedClassifierCV(LinearSVC(dual="auto"), method='sigmoid')) 
    ])
    
    pipeline.fit(X_train, y_train)
    
    # Evaluation
    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    conf_matrix = confusion_matrix(y_test, y_pred).tolist()
    report = classification_report(y_test, y_pred, output_dict=True)
    
    print(f"Model Accuracy: {accuracy:.2f}")
    
    # Save artifacts (Just the pipeline object now, simpler to load!)
    if not os.path.exists('model/artifacts'):
        os.makedirs('model/artifacts')
        
    with open('model/artifacts/pipeline.pkl', 'wb') as f:
        pickle.dump(pipeline, f)
        
    # Save metrics
    metrics = {
        'accuracy': accuracy,
        'confusion_matrix': conf_matrix,
        'classification_report': report
    }
    
    with open('model/artifacts/metrics.json', 'w') as f:
        json.dump(metrics, f)
        
    print("Training complete. Pipeline saved.")

if __name__ == "__main__":
    train_model()
