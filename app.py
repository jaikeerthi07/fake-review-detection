from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
import os
import json
import time
import re
from datetime import datetime
from werkzeug.utils import secure_filename
import requests
from bs4 import BeautifulSoup
from models import db, Review, User
from lie_detector import LieDetector 
from author_dna import AuthorDNA # Added AuthorDNA import # Added LieDetector import

# Initialize App
app = Flask(__name__)
CORS(app) # Enable CORS for React Frontend

# Configuration
IS_VERCEL = os.environ.get('VERCEL') in ['1', 'true', 'True']
# Render usually sets RENDER=true
IS_RENDER = os.environ.get('RENDER') in ['1', 'true', 'True']
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if IS_VERCEL or IS_RENDER:
    # Production / Serverless Environment
    UPLOAD_FOLDER = '/tmp/uploads'
    # Use absolute path to the repo folder
    MODEL_FOLDER = os.path.join(BASE_DIR, 'model', 'artifacts') 
    
    # Database Configuration
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:////tmp/reviews.db'
else:
    # Local Development
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MODEL_FOLDER = os.path.join(BASE_DIR, 'model', 'artifacts')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reviews.db'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'super-secret-key-change-this')
jwt = JWTManager(app)

# Ensure directories exist
for folder in [UPLOAD_FOLDER, MODEL_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# Initialize DB
db.init_app(app)
with app.app_context():
    db.create_all()
    # Execute raw SQL to alter the existing password_hash column length on Render/Postrgres
    # Since SQLAlchemy create_all() doesn't alter existing tables.
    try:
        from sqlalchemy import text
        db.session.execute(text("ALTER TABLE \"user\" ALTER COLUMN password_hash TYPE VARCHAR(256);"))
        db.session.commit()
        print("Successfully ensured password_hash is VARCHAR(256)")
    except Exception as e:
        db.session.rollback()
        print(f"Schema alter skipped or failed: {e}")

# Global variables to hold current state (simple in-memory for demo)
CURRENT_DATASET_PATH = None
TRAINED_MODELS = {}

# --- Helper Functions ---
def load_models():
    """Load models from disk on startup if available"""
    global TRAINED_MODELS
    print(f"Loading models from: {MODEL_FOLDER}...")
    try:
        import pickle
        # Load SVM (Default)
        svm_path = os.path.join(MODEL_FOLDER, 'svm_pipeline.pkl')
        if os.path.exists(svm_path):
            with open(svm_path, 'rb') as f:
                TRAINED_MODELS['SVM'] = pickle.load(f)
        else:
            print(f"Warning: {svm_path} not found")

        # Load NB
        nb_path = os.path.join(MODEL_FOLDER, 'nb_pipeline.pkl')
        if os.path.exists(nb_path):
            with open(nb_path, 'rb') as f:
                TRAINED_MODELS['NaiveBayes'] = pickle.load(f)
        
        # Load LR
        lr_path = os.path.join(MODEL_FOLDER, 'lr_pipeline.pkl')
        if os.path.exists(lr_path):
            with open(lr_path, 'rb') as f:
                TRAINED_MODELS['LogisticRegression'] = pickle.load(f)
                
        print(f"Models loaded successfully. Available models: {list(TRAINED_MODELS.keys())}")
    except Exception as e:
        print(f"CRITICAL: Models error in {MODEL_FOLDER}: {e}")

def load_latest_dataset():
    """Load the most recently uploaded CSV to CURRENT_DATASET_PATH"""
    global CURRENT_DATASET_PATH
    try:
        files = [os.path.join(UPLOAD_FOLDER, f) for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.csv')]
        if files:
            # Prioritize 'fake_review_dataset.csv'
            target_file = next((f for f in files if 'fake_review_dataset.csv' in os.path.basename(f)), None)
            if not target_file:
                target_file = max(files, key=os.path.getctime)
            
            CURRENT_DATASET_PATH = target_file
            print(f"Restored dataset: {CURRENT_DATASET_PATH}")
    except Exception as e:
        print(f"Error restoring dataset: {e}")

load_models()
load_latest_dataset()

# Initialize Analyzers
lie_detector = LieDetector()
author_dna = AuthorDNA()

# --- API Endpoints ---

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "message": "Fake Review Detection Backend is running!",
        "version": "1.0.0"
    }), 200

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f"Register Error: {str(e)}", 'trace': traceback.format_exc()}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password', 'default') # Optional password
        
        print(f"Login attempt for user: {username}")
        print(f"DB URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        # Ensure DB tables exist (Safe-guard for Vercel cold starts)
        try:
            with app.app_context():
                db.create_all()
                print("DB tables checked/created.")
        except Exception as db_e:
            print(f"DB Creation Failed: {db_e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f"Database Init Failed: {str(db_e)}"}), 500

        user = User.query.filter_by(username=username).first()
        
        # Auto-register if user doesn't exist
        if not user:
            print(f"Creating new user: {username}")
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            print("User created.")
        
        # Always allow login (bypass password check)
        access_token = create_access_token(identity=username)
        return jsonify({'access_token': access_token, 'username': username}), 200
    except Exception as e:
        print(f"General Login Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f"Login Error: {str(e)}", 'trace': traceback.format_exc()}), 500

@app.route('/api/debug/models', methods=['GET'])
def debug_models():
    try:
        if not os.path.exists(MODEL_FOLDER):
            return jsonify({'error': f'Model folder does not exist: {MODEL_FOLDER}', 'base_dir': BASE_DIR}), 404
        files = os.listdir(MODEL_FOLDER)
        return jsonify({
            'model_folder': MODEL_FOLDER,
            'files': files,
            'trained_keys': list(TRAINED_MODELS.keys()),
            'exists': os.path.exists(MODEL_FOLDER)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_dataset():
    global CURRENT_DATASET_PATH
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '' or not file.filename.endswith('.csv'):
        return jsonify({'error': 'Invalid file (CSV required)'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    CURRENT_DATASET_PATH = filepath
    
    # Peek at columns
    try:
        import pandas as pd
        df = pd.read_csv(filepath)
        columns = df.columns.tolist()
        return jsonify({'message': 'File uploaded successfully', 'columns': columns, 'filename': filename})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/preview', methods=['GET'])
def preview_data():
    global CURRENT_DATASET_PATH
    if not CURRENT_DATASET_PATH or not os.path.exists(CURRENT_DATASET_PATH):
        return jsonify({'error': 'No dataset uploaded'}), 404
    
    try:
        import pandas as pd
        df = pd.read_csv(CURRENT_DATASET_PATH)
        preview = df.head(10).fillna('').to_dict(orient='records')
        return jsonify({'data': preview, 'total_rows': len(df)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/train', methods=['POST'])
def train_models():
    """Train multiple models and return comparison metrics"""
    global CURRENT_DATASET_PATH, TRAINED_MODELS
    
    data = request.json
    text_col = data.get('text_column', 'text')
    label_col = data.get('label_column', 'label')
    
    if not CURRENT_DATASET_PATH:
        return jsonify({'error': 'No dataset uploaded'}), 400

    try:
        import pandas as pd
        import pickle
        from sklearn.model_selection import train_test_split
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.svm import LinearSVC
        from sklearn.naive_bayes import MultinomialNB
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import Pipeline
        from sklearn.calibration import CalibratedClassifierCV
        from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix

        df = pd.read_csv(CURRENT_DATASET_PATH)
        if text_col not in df.columns or label_col not in df.columns:
            return jsonify({'error': f'Columns {text_col} or {label_col} not found'}), 400
            
        # Preprocessing (Basic)
        df = df.dropna(subset=[text_col, label_col])
        X = df[text_col].astype(str)
        y = df[label_col]
        
        # Train/Test Split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        metrics = {}
        
        # 1. SVM
        svm_pipe = Pipeline([('tfidf', TfidfVectorizer()), ('clf', CalibratedClassifierCV(LinearSVC()))])
        svm_pipe.fit(X_train, y_train)
        y_pred = svm_pipe.predict(X_test)
        metrics['SVM'] = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, average='macro'),
            'recall': recall_score(y_test, y_pred, average='macro'),
            'cm': confusion_matrix(y_test, y_pred).tolist()
        }
        with open(f'{MODEL_FOLDER}/svm_pipeline.pkl', 'wb') as f: pickle.dump(svm_pipe, f)
        TRAINED_MODELS['SVM'] = svm_pipe

        # 2. Naive Bayes
        nb_pipe = Pipeline([('tfidf', TfidfVectorizer()), ('clf', MultinomialNB())])
        nb_pipe.fit(X_train, y_train)
        y_pred = nb_pipe.predict(X_test)
        metrics['NaiveBayes'] = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, pos_label='Fake', average='macro'),
            'recall': recall_score(y_test, y_pred, pos_label='Fake', average='macro'),
            'cm': confusion_matrix(y_test, y_pred).tolist()
        }
        with open(f'{MODEL_FOLDER}/nb_pipeline.pkl', 'wb') as f: pickle.dump(nb_pipe, f)
        TRAINED_MODELS['NaiveBayes'] = nb_pipe
        
        # 3. Logistic Regression
        lr_pipe = Pipeline([('tfidf', TfidfVectorizer()), ('clf', LogisticRegression())])
        lr_pipe.fit(X_train, y_train)
        y_pred = lr_pipe.predict(X_test)
        metrics['LogisticRegression'] = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, pos_label='Fake', average='macro'),
            'recall': recall_score(y_test, y_pred, pos_label='Fake', average='macro'),
            'cm': confusion_matrix(y_test, y_pred).tolist()
        }
        with open(f'{MODEL_FOLDER}/lr_pipeline.pkl', 'wb') as f: pickle.dump(lr_pipe, f)
        TRAINED_MODELS['LogisticRegression'] = lr_pipe

        return jsonify({'message': 'Training complete', 'metrics': metrics})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.json
    text = data.get('text')
    model_name = data.get('model', 'SVM') # Default to SVM
    
    if not text: return jsonify({'error': 'No text provided'}), 400
    
    # Reload models if they are missing (e.g. after a cold start or if load_models fails)
    if not TRAINED_MODELS:
        load_models()
        
    if model_name not in TRAINED_MODELS: 
        available = list(TRAINED_MODELS.keys())
        return jsonify({'error': f'Model {model_name} not found. Available: {available}. Check if model files exist in {MODEL_FOLDER}'}), 500
    
    try:
        model = TRAINED_MODELS[model_name]
        
        # Run selected model
        prediction = model.predict([text])[0]
        proba = model.predict_proba([text])[0]
        classes = model.classes_
        probs = {str(c): float(p) for c, p in zip(classes, proba)}
        confidence = float(max(proba))
    except Exception as e:
        return jsonify({'error': f'Prediction error: {str(e)}'}), 500
    
    # Consensus: Run ALL models
    consensus_votes = {'Fake': 0, 'Real': 0} # Mapping 'CG'->Fake, 'OR'->Real for clarity output?
    # Actually let's stick to dataset labels: CG (Fake), OR (Real)
    model_predictions = {}
    real_prob_sum = 0
    count_models = 0
    
    for m_name, m in TRAINED_MODELS.items():
        try:
            p = m.predict([text])[0]
            model_predictions[m_name] = str(p)
            
            # Trust Score Calculation (Sum prob of 'OR' aka Real)
            p_proba = m.predict_proba([text])[0]
            if 'OR' in m.classes_:
                real_idx = list(m.classes_).index('OR')
                real_prob_sum += p_proba[real_idx]
            else:
                 # Fallback if class names differ
                 real_prob_sum += 0.5 
            count_models += 1
        except:
            pass

    avg_real_prob = real_prob_sum / count_models if count_models > 0 else 0
    trust_score = round(avg_real_prob * 100, 2)
    
    # Lie Detection Analysis
    lie_analysis = lie_detector.analyze(text)
    
    # Author DNA Analysis
    dna_analysis = author_dna.analyze(text)

    # Sentiment Analysis
    from textblob import TextBlob
    sentiment = TextBlob(text).sentiment.polarity
    
    # Save to History
    review = Review(
        text=text, 
        label=str(prediction), 
        confidence=confidence, 
        sentiment=sentiment, 
        timestamp=datetime.now()
    )
    db.session.add(review)
    db.session.commit()
    
    return jsonify({
        'label': str(prediction),
        'confidence': confidence,
        'probs': probs,
        'sentiment': sentiment,
        'model_used': model_name,
        'trust_score': trust_score,
        'model_used': model_name,
        'trust_score': trust_score,
        'consensus': model_predictions,
        'consensus': model_predictions,
        'lie_detection': lie_analysis,
        'author_dna': dna_analysis
    })

@app.route('/api/predict_bulk', methods=['POST'])
def predict_bulk():
    data = request.json
    reviews = data.get('reviews', [])
    model_name = data.get('model', 'SVM')
    
    if not reviews: return jsonify({'error': 'No reviews provided'}), 400
    
    # Reload models if missing
    if not TRAINED_MODELS:
        load_models()
        
    if model_name not in TRAINED_MODELS:
        available = list(TRAINED_MODELS.keys())
        return jsonify({'error': f'Model {model_name} not found. Available: {available}. Check files in {MODEL_FOLDER}'}), 500
    
    model = TRAINED_MODELS[model_name]
    results = []
    
    for item in reviews:
        try:
            # Handle both string and dict input
            if isinstance(item, dict):
                text = item.get('text', '')
                metadata = item
            else:
                text = str(item)
                metadata = {}
                
            # Selected model prediction
            prediction = model.predict([text])[0]
            proba = model.predict_proba([text])[0]
            confidence = float(max(proba))
            from textblob import TextBlob
            sentiment = TextBlob(text).sentiment.polarity
            
            # Trust Score (Simplified for bulk: use selected model's Real prob)
            if 'OR' in model.classes_:
                real_idx = list(model.classes_).index('OR')
                trust_score = float(proba[real_idx]) * 100
            else:
                 trust_score = 50.0 # Fallback
            
            # Lie Detection Analysis
            lie_analysis = lie_detector.analyze(text)
            
            # Author DNA Analysis
            dna_analysis = author_dna.analyze(text)

            result = {
                'text': text,
                'label': str(prediction),
                'confidence': confidence,
                'sentiment': sentiment,
                'trust_score': round(trust_score, 2),
                'lie_detection': lie_analysis,
                'author_dna': dna_analysis
            }
            # Merge metadata (date, rating, author)
            result.update({k: v for k, v in metadata.items() if k != 'text'})
            results.append(result)

        except Exception as e:
            results.append({'text': str(item), 'error': str(e)})
            
    return jsonify({'results': results})

@app.route('/api/scrape', methods=['POST'])
def scrape_reviews():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    # --- UBUY SUPPORT ---
    if 'ubuy' in url.lower():
        print(f"Detected Ubuy URL: {url}")
        try:
            asin = extract_ubuy_asin(url)
            if asin:
                print(f"Extracted ASIN: {asin}, converting to Amazon URL...")
                url = f"https://www.amazon.com/dp/{asin}"
            else:
                 return jsonify({'error': 'Could not extract product ID (ASIN) from Ubuy page'}), 400
        except Exception as e:
            print(f"Ubuy Extraction Failed: {e}")
            return jsonify({'error': f'Failed to process Ubuy URL: {str(e)}'}), 500

    try:
        # --- PRIMARY: Apify Actor ---& Configuration
        APIFY_TOKEN = os.getenv('APIFY_TOKEN', 'YOUR_APIFY_TOKEN_HERE')
        
        actor_config = None
        
        if 'amazon' in url:
            actor_config = {
                'id': 'junglee~amazon-reviews-scraper',
                'input': {
                    "productUrls": [{"url": url}],
                    "maxItems": 20, 
                    "mode": "hcaptcha",
                    "proxyConfiguration": {"useApifyProxy": True}
                },
                'extractor': lambda item: {
                    'text': item.get('reviewDescription'),
                    'rating': item.get('ratingScore'),
                    'title': item.get('reviewTitle'),
                    'author': item.get('reviewAuthor'),
                    'date': item.get('date'),
                    'source': 'Amazon'
                }
            }
        elif 'flipkart' in url:
            # Fallback/Experimental for Flipkart
            # Note: Most Flipkart actors (e.g., easyapi, codingfrontend) are now paid.
            # Returning a friendly error until a free actor is found or subscription is added.
            return jsonify({
                'error': 'Flipkart scraping currently requires a paid API subscription. Please use Amazon URLs or paste the review text manually.'
            }), 400
            
            # Legacy/Paid Configuration (Kept for reference if upgraded)
            # actor_config = {
            #     'id': 'easyapi~flipkart-review-scraper', 
            #     'input': { ... }
            # }
        else:
            return jsonify({'error': 'Unsupported platform. Currently supporting Amazon.'}), 400

        # 1. Start the Actor Run
        run_url = f'https://api.apify.com/v2/acts/{actor_config["id"]}/runs?token={APIFY_TOKEN}'
        
        try:
            response = requests.post(run_url, json=actor_config['input'], timeout=10)
            if response.status_code == 201:
                run_data = response.json()['data']
                run_id = run_data['id']
                dataset_id = run_data['defaultDatasetId']
                
                # Poll
                for _ in range(30):
                    time.sleep(2)
                    status_res = requests.get(f'https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_TOKEN}')
                    if status_res.status_code == 200 and status_res.json()['data']['status'] == 'SUCCEEDED':
                        items_res = requests.get(f'https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}')
                        if items_res.status_code == 200:
                            items = items_res.json()
                            if items:
                                # reviews = [actor_config['extractor'](i)['text'] for i in items if actor_config['extractor'](i)['text']]
                                # ENTERPRISE UPGRADE: Return full object
                                reviews = [actor_config['extractor'](i) for i in items if actor_config['extractor'](i).get('text')]
                                
                                if reviews:
                                    return jsonify({'reviews': reviews[:50], 'count': len(reviews), 'csv_saved': save_csv(reviews)})
                        break
        except Exception as e:
            print(f"Apify failed, switching to fallback: {e}")

        # --- FALLBACK: Direct BeautifulSoup Hand-Curated Scraping ---
        print("Using Fallback Scraper...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        try:
            res = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # Target standard Amazon review elements
            review_elements = soup.select('div[data-hook="review"]')
            
            # Fallback if standard hook is missing (common in some locales/layouts)
            if not review_elements:
                print("Standard 'review' hook not found. Trying 'customer_review' ID...")
                review_elements = soup.select('div[id^="customer_review"]')
                
            print(f"Found {len(review_elements)} review elements.")
            
            reviews = []
            
            for review in review_elements:
                # Text
                body = review.select_one('span[data-hook="review-body"]')
                if not body:
                    continue
                    
                review_text = body.get_text().strip()
                if not review_text:
                    continue 

                # Title
                title = "No Title"
                title_el = review.select_one('a[data-hook="review-title"]')
                if title_el:
                    title = title_el.get_text().strip()
                
                # Rating
                rating = None
                try:
                    rating_el = review.select_one('i[data-hook="review-star-rating"]') or \
                                review.select_one('i[data-hook="cmps-review-star-rating"]')
                    if rating_el:
                        rating_text = rating_el.get_text().strip() # "4.0 out of 5 stars"
                        rating = float(rating_text.split(' ')[0])
                except Exception as e:
                    print(f"Error parsing rating: {e}")
                
                # Date
                date_str = None
                try:
                    date_el = review.select_one('span[data-hook="review-date"]')
                    if date_el:
                        date_text = date_el.get_text().strip()
                        # Format: "Reviewed in the United States on January 1, 2024"
                        if ' on ' in date_text:
                            date_str = date_text.split(' on ')[-1]
                        else:
                            date_str = date_text # Fallback
                except Exception as e:
                    print(f"Error parsing date: {e}")

                reviews.append({
                    'text': review_text,
                    'title': title,
                    'rating': rating,
                    'date': date_str,
                    'source': 'Amazon (Fallback)'
                })
            
            if reviews:
                 return jsonify({'reviews': reviews, 'count': len(reviews), 'csv_saved': save_csv(reviews)})
            else:
                 # User requested mixed reviews (real and fake) for demonstration purposes if live scraping fails
                 print("Applying mock fallback reviews for demonstration...")
                 mock_reviews = [
                     {
                         'text': 'This product is absolutely amazing! I have been using it for weeks and it exceeded all my expectations. Highly recommended!',
                         'title': 'Great Purchase',
                         'rating': 5.0,
                         'date': 'January 10, 2024',
                         'source': 'Amazon (Mock)'
                     },
                     {
                         'text': 'Terrible quality. Broke after one use. Do not buy this garbage, waste of money.',
                         'title': 'Do not buy',
                         'rating': 1.0,
                         'date': 'February 5, 2024',
                         'source': 'Amazon (Mock)'
                     },
                     {
                         'text': 'I was paid to write this review. It is a very good product and I love it so much. Please buy it.',
                         'title': 'Very good product',
                         'rating': 5.0,
                         'date': 'March 12, 2024',
                         'source': 'Amazon (Mock)'
                     },
                     {
                         'text': 'Decent product for the price. Does what it says, but nothing spectacular. Good value overall.',
                         'title': 'Okay',
                         'rating': 3.0,
                         'date': 'April 20, 2024',
                         'source': 'Amazon (Mock)'
                     }
                 ]
                 return jsonify({'reviews': mock_reviews, 'count': len(mock_reviews), 'csv_saved': save_csv(mock_reviews)})

        except Exception as e:
             return jsonify({'error': f"Fallback failed: {str(e)}"}), 500

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f"Scraping error: {str(e)}"}), 500

def extract_ubuy_asin(ubuy_url):
    """
    Fetches Ubuy product page and extracts the underlying Amazon ASIN.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    }
    
    print(f"Fetching Ubuy Page: {ubuy_url}")
    res = requests.get(ubuy_url, headers=headers, timeout=15)
    
    if res.status_code != 200:
        raise Exception(f"Ubuy Page Load Failed: {res.status_code}")
        
    # Look for 'var selected_asin = "B0..."'
    # Pattern: var selected_asin = 'B0FNCGKF6Q';
    match = re.search(r"var selected_asin\s*=\s*['\"]([^'\"]+)['\"];", res.text)
    if match:
        return match.group(1)
        
    # Fallback: parent_asin
    match_parent = re.search(r"var parent_asin\s*=\s*['\"]([^'\"]+)['\"];", res.text)
    if match_parent:
         return match_parent.group(1)
         
    return None

def save_csv(reviews):
    """Helper to save reviews to CSV"""
    if not reviews: return None
    
    # Handle list of dicts or list of strings
    if reviews and isinstance(reviews[0], dict):
        import pandas as pd
        df = pd.DataFrame(reviews)
    else:
        import pandas as pd
        df = pd.DataFrame({'text': reviews})
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'scraped_reviews_{timestamp}.csv'
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df.to_csv(filepath, index=False)
    return filename

@app.route('/api/history', methods=['GET'])
def get_history():
    reviews = Review.query.order_by(Review.timestamp.desc()).limit(50).all()
    return jsonify([r.to_dict() for r in reviews])

@app.route('/api/model/features', methods=['GET'])
def get_model_features():
    """Extract top 20 positive and negative features from the model"""
    model_name = request.args.get('model', 'SVM')
    if model_name not in TRAINED_MODELS:
        return jsonify({'error': 'Model not found'}), 400
        
    pipeline = TRAINED_MODELS[model_name]
    try:
        # Check if pipeline has a linear model with coefficients
        vectorizer = pipeline.named_steps['tfidf']
        classifier = pipeline.named_steps['clf']
        
        # Handle CalibratedClassifierCV wrapper for SVM
        if hasattr(classifier, 'calibrated_classifiers_'):
            # Use the estimator of the first calibrated classifier
            cc = classifier.calibrated_classifiers_[0]
            if hasattr(cc, 'estimator'):
                classifier = cc.estimator
            elif hasattr(cc, 'base_estimator'):
                classifier = cc.base_estimator
            
        if not hasattr(classifier, 'coef_'):
             return jsonify({'error': 'Model does not support feature extraction (no coefficients)'}), 400
             
        feature_names = vectorizer.get_feature_names_out()
        import numpy as np
        coefs = classifier.coef_[0]
        
        # Get top 10 positive (Fake) and top 10 negative (Real)
        top_positive_indices = np.argsort(coefs)[-10:]
        top_negative_indices = np.argsort(coefs)[:10]
        
        features = []
        for idx in top_positive_indices:
            features.append({'name': feature_names[idx], 'impact': float(coefs[idx]), 'type': 'Fake'})
            
        for idx in top_negative_indices:
            features.append({'name': feature_names[idx], 'impact': float(coefs[idx]), 'type': 'Real'})
            
        return jsonify({'features': features})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Compute dataset statistics for charts"""
    global CURRENT_DATASET_PATH
    if not CURRENT_DATASET_PATH:
        return jsonify({'error': 'No dataset uploaded'}), 400
        
    try:
        import pandas as pd
        from textblob import TextBlob
        df = pd.read_csv(CURRENT_DATASET_PATH)
        # Assume columns 'text', 'label', 'rating' exist or try to find them
        text_col = next((c for c in df.columns if 'text' in c.lower() or 'review' in c.lower()), 'text')
        label_col = next((c for c in df.columns if 'label' in c.lower() or 'category' in c.lower()), 'label')
        
        if text_col not in df.columns:
            return jsonify({'error': 'Text column not found'}), 400
            
        # 1. Authenticity Distribution
        if label_col in df.columns:
            auth_dist = df[label_col].value_counts().to_dict()
        else:
            auth_dist = {}
            
        # 2. Vocabulary Richness (Avg unique words / total words)
        def get_richness(text):
            words = str(text).split()
            if not words: return 0
            return len(set(words)) / len(words)
            
        df['richness'] = df[text_col].apply(get_richness)
        avg_richness = float(df['richness'].mean())
        
        # 3. Sentence Count Distribution
        def get_sentence_count(text):
            return len(TextBlob(str(text)).sentences)
            
        df['sentence_count'] = df[text_col].apply(get_sentence_count)
        # Bucketize
        sent_counts = df['sentence_count'].value_counts(bins=5, sort=False).to_dict()
        # Convert interval keys to string
        sent_dist = {str(k): int(v) for k, v in sent_counts.items()}
        
        # 4. Rating vs Authenticity Distribution
        rating_auth_dist = []
        rating_col = next((c for c in df.columns if 'rating' in c.lower() or 'star' in c.lower()), None)
        
        if rating_col and label_col in df.columns:
            # Group by rating and label
            # Ensure ratings are sorted
            unique_ratings = sorted(df[rating_col].dropna().unique())
            for r in unique_ratings:
                # Get subset for this rating
                subset = df[df[rating_col] == r]
                counts = subset[label_col].value_counts().to_dict()
                
                fake_count = counts.get('CG', 0) + counts.get('Fake', 0)
                real_count = counts.get('OR', 0) + counts.get('Real', 0)
                
                rating_auth_dist.append({
                    'rating': str(r),
                    'Real': int(real_count),
                    'Fake': int(fake_count)
                })
        # If simpler rating_dist matches
        elif rating_col:
             counts = df[rating_col].value_counts().sort_index().to_dict()
             rating_auth_dist = [{'rating': str(k), 'Count': int(v)} for k,v in counts.items()]
        else:
            # Fallback: Infer rating from sentiment if column is missing
            try:
                def get_polarity(text):
                    return TextBlob(str(text)).sentiment.polarity
                
                df['polarity'] = df[text_col].apply(get_polarity)
                
                # Use rank-based bucketing to handle duplicate polarity values
                # pct=True gives rank as a fraction 0-1, then multiply by 5 and ceil to get 1-5
                df['inferred_rating'] = (df['polarity'].rank(pct=True) * 5).apply(lambda x: min(int(x) + 1, 5))
                
                # Check if label exists for grouping
                if label_col in df.columns:
                     for r in [1, 2, 3, 4, 5]:
                        subset = df[df['inferred_rating'] == r]
                        counts = subset[label_col].value_counts().to_dict()
                        fake = counts.get('CG', 0) + counts.get('Fake', 0)
                        real = counts.get('OR', 0) + counts.get('Real', 0)
                        rating_auth_dist.append({'rating': f'{r} Star', 'Real': int(real), 'Fake': int(fake)})
                else:
                     counts = df['inferred_rating'].value_counts().sort_index().to_dict()
                     rating_auth_dist = [{'rating': f'{k} Star', 'Count': int(v)} for k,v in counts.items()]
            except Exception as e:
                print(f"Error inferring ratings: {e}")

        # 5. Sentiment Trend
        sentiment_trend = []
        date_col = next((c for c in df.columns if 'date' in c.lower() or 'time' in c.lower()), None)
        
        if date_col:
            try:
                # Ensure date column is datetime
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                # Drop invalid dates
                temp_df = df.dropna(subset=[date_col])
                
                # Calculate polarity if not already done
                if 'polarity' not in temp_df.columns:
                     temp_df['polarity'] = temp_df[text_col].apply(lambda x: TextBlob(str(x)).sentiment.polarity)
                
                # Group by date (daily) and take mean sentiment
                trend = temp_df.groupby(temp_df[date_col].dt.strftime('%Y-%m-%d'))['polarity'].mean().reset_index()
                trend.columns = ['date', 'sentiment']
                sentiment_trend = trend.to_dict(orient='records')
                # Sort by date
                sentiment_trend.sort(key=lambda x: x['date'])
            except Exception as e:
                print(f"Error computing trend: {e}")

        return jsonify({
            'authenticity': auth_dist,
            'vocabulary_richness': avg_richness,
            'sentence_distribution': sent_dist,
            'rating_distribution': rating_auth_dist,
            'sentiment_trend': sentiment_trend
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/preview', methods=['GET'])
def get_preview():
    """Return a preview of the currently uploaded dataset"""
    global CURRENT_DATASET_PATH
    if not CURRENT_DATASET_PATH:
        return jsonify({'error': 'No dataset uploaded'}), 400
    
    try:
        df = pd.read_csv(CURRENT_DATASET_PATH)
        # Limit preview to 10 rows and handle NaN for JSON serialization
        preview_data = df.head(10).fillna('').to_dict(orient='records')
        return jsonify({'data': preview_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """Download a file from the upload folder"""
    try:
        return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/api/report/generate', methods=['POST'])
def generate_pdf_report():
    data = request.json
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
        
    try:
        from report_generator import generate_report
        
        # Ensure uploads folder exists
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"TrustLens_Audit_{timestamp}.pdf"
        
        filepath = generate_report(data, filename)
        
        # Return the filename so frontend can request download
        return jsonify({'filename': filename, 'message': 'Report generated successfully'})
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f"Report generation failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
