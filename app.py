# Deployment Timestamp: 2026-03-25T01:00:00Z - Stability Fix V3
# Optimize NLTK for Vercel (Download to /tmp)
import nltk
import os
NLTK_DATA_PATH = '/tmp/nltk_data'
os.makedirs(NLTK_DATA_PATH, exist_ok=True)
if NLTK_DATA_PATH not in nltk.data.path:
    nltk.data.path.append(NLTK_DATA_PATH)

def download_nltk_capsule():
    for pkg in ['stopwords', 'punkt', 'punkt_tab', 'averaged_perceptron_tagger_eng']:
        try:
            nltk.data.find(f'corpora/{pkg}' if pkg == 'stopwords' else f'tokenizers/{pkg}' if 'punkt' in pkg else f'taggers/{pkg}')
        except LookupError:
            nltk.download(pkg, download_dir=NLTK_DATA_PATH)

download_nltk_capsule()

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
import json
import time
import re
from datetime import datetime
from werkzeug.utils import secure_filename
import requests
from bs4 import BeautifulSoup
from models import db, Review, User
from lie_detector import LieDetector 
from author_dna import AuthorDNA

# Initialize App
app = Flask(__name__)
CORS(app) # Enable CORS for React Frontend

# Configuration
# Fail-safe Vercel detection: look for Vercel env vars OR the /var/task deployment root
IS_VERCEL = os.environ.get('VERCEL') == '1' or 'VERCEL' in os.environ or os.path.exists('/var/task')
IS_RENDER = os.environ.get('RENDER') in ['1', 'true', 'True']
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if IS_VERCEL or IS_RENDER:
    # Production / Serverless Environment
    UPLOAD_FOLDER = '/tmp/uploads'
    # Models are saved to /tmp during training, then read from there.
    MODEL_FOLDER = '/tmp/model_artifacts' 
    
    # Database Configuration
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        elif database_url.startswith("mysql://"):
            database_url = database_url.replace("mysql://", "mysql+pymysql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:////tmp/reviews.db'
else:
    # Local Development
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MODEL_FOLDER = os.path.join(BASE_DIR, 'model', 'artifacts')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reviews.db'

# Ensure writable directories exist (with fail-safe for read-only environments)
def ensure_dir_exists(path):
    try:
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            print(f"Created directory: {path}")
    except OSError as e:
        print(f"Warning: Could not create {path}: {e}")

if IS_VERCEL or IS_RENDER:
    ensure_dir_exists(UPLOAD_FOLDER)
else:
    for folder in [UPLOAD_FOLDER, MODEL_FOLDER]:
        ensure_dir_exists(folder)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'super-secret-key-change-this')
jwt = JWTManager(app)

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
        # On Vercel, try loading from /tmp first (newly trained), then fallback to repo (defaults)
        REPO_MODEL_FOLDER = os.path.join(BASE_DIR, 'model', 'artifacts')
        
        for model_name, filename in [('SVM', 'svm_pipeline.pkl'), ('NaiveBayes', 'nb_pipeline.pkl'), ('LogisticRegression', 'lr_pipeline.pkl')]:
            # Try /tmp first
            path = os.path.join(MODEL_FOLDER, filename)
            if not os.path.exists(path):
                # Fallback to repo
                path = os.path.join(REPO_MODEL_FOLDER, filename)
            
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    TRAINED_MODELS[model_name] = pickle.load(f)
                    print(f"Loaded {model_name} from {path}")
            else:
                print(f"Warning: model {model_name} not found in {MODEL_FOLDER} or {REPO_MODEL_FOLDER}")

        print(f"Models loaded successfully. Available models: {list(TRAINED_MODELS.keys())}")
    except Exception as e:
        print(f"CRITICAL: Models loading error: {e}")

def load_latest_dataset():
    """Load the most recently uploaded CSV to CURRENT_DATASET_PATH"""
    global CURRENT_DATASET_PATH
    try:
        # Check /tmp first
        files = []
        if os.path.exists(UPLOAD_FOLDER):
            files = [os.path.join(UPLOAD_FOLDER, f) for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.csv')]
            
        if files:
            # Prioritize 'fake_review_dataset.csv' in /tmp if it was just uploaded
            target_file = next((f for f in files if 'fake_review_dataset.csv' in os.path.basename(f)), None)
            if not target_file:
                target_file = max(files, key=os.path.getmtime)
            
            CURRENT_DATASET_PATH = target_file
            print(f"Restored session dataset: {CURRENT_DATASET_PATH}")
        else:
            # Fallback to repo baseline
            repo_baseline = os.path.join(BASE_DIR, 'uploads', 'fake_review_dataset.csv')
            if os.path.exists(repo_baseline):
                CURRENT_DATASET_PATH = repo_baseline
                print(f"Using repo baseline dataset: {CURRENT_DATASET_PATH}")
            else:
                print(f"Warning: No dataset found in {UPLOAD_FOLDER} or {repo_baseline}")
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
            
        # Subset data for Vercel to avoid 10s timeout
        if IS_VERCEL and len(df) > 200:
            df = df.sample(n=200, random_state=42)
            print("Vercel mode: subsetted to 200 rows for fast training.")
            
        # Preprocessing (Basic)
        df = df.dropna(subset=[text_col, label_col])
        X = df[text_col].astype(str)
        y = df[label_col]
        
        # Train/Test Split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        metrics = {}
        
        # Ensure model folder exists
        ensure_dir_exists(MODEL_FOLDER)
        
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
@jwt_required(optional=True)
def predict():
    try:
        data = request.json
        text = data.get('text', '')
        model_name = data.get('model', 'SVM') # Default to SVM
        
        if not text: return jsonify({'error': 'No text provided'}), 400
        
        # Reload models if they are missing
        if not TRAINED_MODELS:
            load_models()
            
        if model_name not in TRAINED_MODELS: 
            available = list(TRAINED_MODELS.keys())
            return jsonify({'error': f'Model {model_name} not found. Available: {available}. Check if model files exist in {MODEL_FOLDER}'}), 500
        
        model = TRAINED_MODELS[model_name]

        # === RUN MODEL FIRST (must happen before label mapping) ===
        prediction = model.predict([text])[0]
        proba = model.predict_proba([text])[0]
        classes = model.classes_
        probs = {str(c): float(p) for c, p in zip(classes, proba)}
        confidence = float(max(proba))
        
        # Label Mapping (Comprehensive: handles CG/OR codes and 0/1 integers)
        label_raw = str(prediction).upper()
        if label_raw in ['1', 'CG', 'FAKE']:
            label_display = "Fake"
        elif label_raw in ['0', 'OR', 'REAL']:
            label_display = "Real"
        else:
            label_display = label_raw  # Fallback for unknown codes

        # Consensus: Run ALL models and normalize to Fake/Real labels
        model_predictions = {}
        consensus_votes = {'Fake': 0, 'Real': 0}
        for name, m in TRAINED_MODELS.items():
            if hasattr(m, 'predict'):
                pred = m.predict([text])[0]
                # Map consensus votes
                p_str = str(pred).upper()
                vote_label = 'Real' if p_str in ['0', 'OR', 'REAL'] else 'Fake'
                model_predictions[name] = vote_label
                consensus_votes[vote_label] += 1
        
        # Trust Score
        if 'OR' in model.classes_:
            real_idx = list(model.classes_).index('OR')
            trust_score = float(proba[real_idx]) * 100
        elif 0 in model.classes_:
            real_idx = list(model.classes_).index(0)
            trust_score = float(proba[real_idx]) * 100
        else:
            trust_score = 50.0

        # Lie Detection Analysis
        lie_analysis = lie_detector.analyze(text)
        
        # Author DNA Analysis
        dna_analysis = author_dna.analyze(text)

        # Sentiment Analysis
        from textblob import TextBlob
        sentiment = TextBlob(text).sentiment.polarity
        
        # Save to History
        try:
            review = Review(
                text=text, 
                label=str(prediction), 
                confidence=confidence, 
                sentiment=sentiment, 
                timestamp=datetime.now()
            )
            db.session.add(review)
            db.session.commit()
        except Exception as db_err:
            print(f"Database error: {db_err}")
            db.session.rollback()
            # We continue even if DB save fails, just to return the prediction

        return jsonify({
            'label': label_display,
            'confidence': confidence,
            'probs': probs,
            'sentiment': sentiment,
            'model_used': model_name,
            'trust_score': trust_score,
            'consensus': model_predictions,
            'lie_detection': lie_analysis,
            'author_dna': dna_analysis
        })

    except Exception as e:
        print(f"Prediction Error: {e}")
        return jsonify({'error': 'Prediction failed. Check server logs.'}), 500

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
            
            # Label Mapping
            label_raw = str(prediction).upper()
            if label_raw in ['1', 'CG', 'FAKE']:
                label_display = "Fake"
            elif label_raw in ['0', 'OR', 'REAL']:
                label_display = "Real"
            else:
                label_display = label_raw

            # Trust Score
            if 'OR' in model.classes_:
                real_idx = list(model.classes_).index('OR')
                trust_score = float(proba[real_idx]) * 100
            elif 0 in model.classes_:
                real_idx = list(model.classes_).index(0)
                trust_score = float(proba[real_idx]) * 100
            else:
                 trust_score = 50.0 # Fallback
            
            # Lie Detection Analysis
            lie_analysis = lie_detector.analyze(text)
            
            # Author DNA Analysis
            dna_analysis = author_dna.analyze(text)

            result = {
                'text': text,
                'label': label_display,
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

def generate_synthetic_reviews(scraped_reviews, platform="Amazon", count=10):
    """
    Injects realistic synthetic 'fake' reviews into the scraped data to provide 
    a mixed dataset for demonstration and testing.
    """
    import random
    
    fake_review_templates = [
        {"text": "BEST PRODUCT EVER!! I AM SO HAPPY WITH THIS PURCHASE. BUY IT NOW OR YOU WILL REGRET IT. AWESOME AWESOME AWESOME!!!", "title": "AMAZING!!!", "rating": 5.0},
        {"text": "SCAM ALERT! This is a total fraud. I lost my money and the product never arrived. Do not trust this seller, they are thieves.", "title": "TOTAL SCAM", "rating": 1.0},
        {"text": "I was paid $50 to write this review but honestly the product is garbage. Don't believe the high ratings, they are all bought.", "title": "Paid review", "rating": 1.0},
        {"text": "Literally changed my life. I can't believe how good this is. Seriously, stop reading and just add to cart immediately!", "title": "LIFE CHANGING", "rating": 5.0},
        {"text": "Terrible quality. Broke in one day. Customer service is a nightmare. Keep your distance from this trash product.", "title": "STAY AWAY", "rating": 1.0},
        {"text": "I work for this company and I can tell you we make junk. These positive reviews are all from our marketing team. Scam!!", "title": "Employee leaking truth", "rating": 1.0},
        {"text": "WOW WOW WOW!! Best thing I have ever owned. The quality is top notch and the shipping was lightning fast. Must buy!!", "title": "WOW!!!", "rating": 5.0},
        {"text": "Absolute waste of time. Doesn't work as advertised. The box was empty when it arrived and they won't refund me. FRAUD!!", "title": "FRAUD", "rating": 1.0},
        {"text": "Simply the best. Better than all the competitors. I've tried them all and this is the clear winner for everyone.", "title": "Number One", "rating": 5.0},
        {"text": "The instructions are impossible. I spent 4 hours trying to set it up and it still doesn't work. I am returning this immediately.", "title": "Too complicated", "rating": 2.0},
        {"text": "Best investment of the year. It's so efficient and stylish. Everyone asks me where I got it. Highly recommend to all!", "title": "Stunning", "rating": 5.0},
        {"text": "Product arrived used and dirty with someone else's hair on it. Disgusting. I am never buying from this brand again.", "title": "REVOLTING", "rating": 1.0},
        {"text": "FASTEST SHIPPING EVER!! I ordered it and it was at my door in 2 hours. The product is also perfect in every possible way.", "title": "IMPRESSED", "rating": 5.0},
        {"text": "Overpriced garbage. You can get the same thing for 1/10th the price at any local store. Don't fall for the branding hype.", "title": "RIP OFF", "rating": 1.0},
        {"text": "Incredibile design and performance. I use it constantly throughout the day and it never fails me. Absolute perfection.", "title": "PERFECT", "rating": 5.0},
        {"text": "Crashes my phone every time I use it. The app is full of bugs and the hardware is even worse. Total disaster.", "title": "DISASTER", "rating": 1.0},
        {"text": "Most amazing gift I've ever given. My wife was so happy she cried. Thank you for making such a wonderful product!!", "title": "LOVED IT", "rating": 5.0},
        {"text": "The battery exploded while charging! This is dangerous and should be banned. I almost lost my house. LAW SUIT COMING!!", "title": "DANGEROUS", "rating": 1.0},
        {"text": "The product is decent but has a few flaws. The build quality could be better for the price, but it gets the job done overall.", "title": "Okay for the price", "rating": 3.0},
        {"text": "I've been using this for a few weeks now. It works exactly as described. The battery life is surprisingly good, though the setup took me a bit of time.", "title": "Solid performance but difficult setup", "rating": 4.0},
        {"text": "Not exactly what I was expecting. It works, but honestly the material feels a bit cheap. I'll probably keep it since returning is a hassle.", "title": "Just alright", "rating": 3.0},
        {"text": "After reading the reviews, I bought this. It arrived on time. The packaging was neat, and it functions normally. No complaints so far.", "title": "Does the job", "rating": 4.0},
        {"text": "Purchased this for my home office. It fits perfectly and seems sturdy enough. The color matches the pictures online.", "title": "Good purchase", "rating": 5.0},
        {"text": "Unfortunately, it broke after two months of regular use. The hinges are weak. I contacted customer support and they offered a partial refund.", "title": "Broke quickly", "rating": 2.0}
    ]

    synthetic_reviews = []
    source_name = f"{platform} (Synthetic)"
    
    # Shuffle and pick unique templates
    random.shuffle(fake_review_templates)
    pool = fake_review_templates[:count] if count <= len(fake_review_templates) else fake_review_templates
    
    for template in pool:
        review = template.copy()
        # Add slight string variations to avoid identical text across multiple runs
        prefix = random.choice(["", "Literally, ", "Honestly, ", "Actually, ", "I think "])
        review['text'] = prefix + review['text']
        review['date'] = datetime.now().strftime("%B %d, %Y")
        review['author'] = random.choice(["User_" + str(random.randint(100, 999)), "Verified Buyer", "Reviewer_" + str(random.randint(10, 99))])
        review['source'] = source_name
        synthetic_reviews.append(review)
        
    return scraped_reviews + synthetic_reviews

@app.route('/api/scrape', methods=['POST'])
def scrape_reviews():
    data = request.json
    url = data.get('url')
    max_items = data.get('max_items', 20) # Default to 20
    
    # Cap max_items for safety/performance
    max_items = min(int(max_items), 500)
    
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
                    "maxItems": max_items, 
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
            # Flipkart Support via Apify Actor
            actor_config = {
                'id': 'codingfrontend~flipkart-reviews-scraper',
                'input': {
                    "startUrls": [{"url": url}],
                    "maxItems": max_items,
                    "proxyConfiguration": {"useApifyProxy": True}
                },
                'extractor': lambda item: {
                    'text': item.get('text'),
                    'rating': item.get('rating'),
                    'title': item.get('title'),
                    'author': item.get('author'),
                    'date': item.get('date'),
                    'source': 'Flipkart'
                }
            }
        else:
            actor_config = None
            
        supported = ['amazon', 'flipkart', 'myntra', 'meesho', 'ajio', 'bigbasket', 'biggest', 'nykaa', 'shopsy']
        url_lower = url.lower()
        if not any(p in url_lower for p in supported):
            return jsonify({'error': 'Unsupported platform. Check URL.'}), 400

        # Platform Detection for Fallback
        if 'flipkart' in url_lower: platform_name = "Flipkart"
        elif 'myntra' in url_lower: platform_name = "Myntra"
        elif 'meesho' in url_lower: platform_name = "Meesho"
        elif 'ajio' in url_lower: platform_name = "Ajio"
        elif 'bigbasket' in url_lower or 'biggest' in url_lower: platform_name = "BigBasket"
        elif 'nykaa' in url_lower: platform_name = "Nykaa"
        elif 'shopsy' in url_lower: platform_name = "Shopsy"
        else: platform_name = "Amazon"

        try:
            if actor_config:
                # 1. Start the Actor Run
                run_url = f'https://api.apify.com/v2/acts/{actor_config["id"]}/runs?token={APIFY_TOKEN}'
                response = requests.post(run_url, json=actor_config['input'], timeout=10)
            else:
                response = None
                
            if response and response.status_code == 201:
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
            
            # Fallback for Amazon
            if not review_elements and 'amazon' in url:
                print("Standard 'review' hook not found. Trying 'customer_review' ID...")
                review_elements = soup.select('div[id^="customer_review"]')

            # Target Flipkart review elements (common classes and new ones from subagent)
            if not review_elements and 'flipkart' in url:
                print("Targeting Flipkart review classes...")
                # Try dedicated page classes first, then preview classes
                review_elements = soup.select('div.css-175oi2r') or \
                                 soup.select('div._1psv1zeir') or \
                                 soup.select('div.col._2sc7S_') or \
                                 soup.select('div._27M-N_') or \
                                 soup.select('div.t-ZTKy')

            # Target New Platform Elements (Basic effort, heavily reliance on Synthetic generator due to bot protections)
            if not review_elements:
                if 'myntra' in url: review_elements = soup.select('div.user-review-main')
                elif 'meesho' in url: review_elements = soup.select('div.sc-ezOQGI', limit=10) # generic
                elif 'ajio' in url: review_elements = soup.select('div.review-wrapper')
                elif 'bigbasket' in url or 'biggest' in url: review_elements = soup.select('div.review-content')
                elif 'nykaa' in url: review_elements = soup.select('div.review-box')
                elif 'shopsy' in url: review_elements = soup.select('div.t-ZTKy')

            print(f"Found {len(review_elements)} review elements. Limiting to {max_items}.")
            review_elements = review_elements[:max_items]
            
            reviews = []
            
            for review in review_elements:
                review_text = ""
                title = "No Title"
                rating = None
                date_str = datetime.now().strftime("%B %d, %Y")

                if 'amazon' in url:
                    # Amazon Text
                    body = review.select_one('span[data-hook="review-body"]')
                    if body: review_text = body.get_text().strip()
                    
                    # Amazon Title
                    title_el = review.select_one('a[data-hook="review-title"]')
                    if title_el: title = title_el.get_text().strip()
                    
                    # Amazon Rating
                    rating_el = review.select_one('i[data-hook="review-star-rating"]') or \
                                review.select_one('i[data-hook="cmps-review-star-rating"]')
                    if rating_el:
                        try:
                            rating_text = rating_el.get_text().strip()
                            rating = float(rating_text.split(' ')[0])
                        except: pass
                    
                    # Amazon Date
                    date_el = review.select_one('span[data-hook="review-date"]')
                    if date_el:
                        date_text = date_el.get_text().strip()
                        if ' on ' in date_text: date_str = date_text.split(' on ')[-1]

                elif 'flipkart' in url:
                    # Flipkart Text (Trying multiple possibilities)
                    body = review.select_one('span.css-1qaijid') or \
                           review.select_one('a._1psv1zeex') or \
                           review.select_one('.t-ZTKy') or \
                           review.select_one('div.text')
                    if body: review_text = body.get_text().replace('READ MORE', '').strip()
                    
                    # Flipkart Title
                    title_el = review.select_one('div.css-1rynq56') or \
                               review.select_one('div._1psv1zeko') or \
                               review.select_one('p._2-N1Y1') or \
                               review.select_one('._2Wk9S_')
                    if title_el: title = title_el.get_text().strip()
                    
                    # Flipkart Rating
                    rating_el = review.select_one('div._3LWZlK') or \
                                review.select_one('div._1BLS3D') or \
                                review.select_one('div._7dzyg26')
                    if rating_el:
                        try:
                            # Extract first number from text
                            import re
                            rating_match = re.search(r'\d+(\.\d+)?', rating_el.get_text())
                            if rating_match:
                                rating = float(rating_match.group())
                        except: pass
                    
                    # Flipkart Date
                    date_el = review.select_one('div._1psv1zeef') or (review.select_all('p._2sc7S_ span')[-1] if hasattr(review, 'select_all') and review.select_all('p._2sc7S_ span') else None)
                    if date_el: date_str = date_el.get_text().strip()
                
                # New Platform Fallbacks (Best effort HTML parsing, mainly relies on synthetic fallbacks for demo)
                elif 'myntra' in url:
                    body = review.select_one('div.user-review-main')
                    if body: review_text = body.get_text().strip()
                elif 'meesho' in url:
                    body = review.select_one('div.sc-ezOQGI, div.review-text')
                    if body: review_text = body.get_text().strip()
                elif 'ajio' in url:
                    body = review.select_one('div.review-wrapper, div.review-content')
                    if body: review_text = body.get_text().strip()
                elif 'bigbasket' in url or 'biggest' in url:
                    body = review.select_one('div.review-content, p.desc')
                    if body: review_text = body.get_text().strip()
                elif 'nykaa' in url:
                    body = review.select_one('div.review-box, p.review-desc')
                    if body: review_text = body.get_text().strip()
                elif 'shopsy' in url:
                    body = review.select_one('.t-ZTKy, div.text')
                    if body: review_text = body.get_text().replace('READ MORE', '').strip()

                if not review_text:
                    continue 

                reviews.append({
                    'text': review_text,
                    'title': title,
                    'rating': rating,
                    'date': date_str,
                    'source': f'{platform_name} (Fallback)'
                })

            # --- Myntra API Fallback ---
            if not reviews and 'myntra' in url_lower:
                print("Trying Myntra API Fallback...")
                try:
                    match = re.search(r'/(\d+)/buy', url)
                    if match:
                        product_id = match.group(1)
                        review_url = f"https://www.myntra.com/gateway/v2/product/{product_id}/reviews"
                        api_res = requests.get(review_url, headers=headers, timeout=5)
                        if api_res.status_code == 200:
                            api_data = api_res.json()
                            for r in api_data.get('reviews', []):
                                reviews.append({
                                    'text': r.get('reviewText', ''),
                                    'title': r.get('headline', 'No Title'),
                                    'rating': r.get('rating', 0),
                                    'date': r.get('date', datetime.now().strftime("%B %d, %Y")),
                                    'source': 'Myntra (API)'
                                })
                except Exception as api_e:
                    print(f"Myntra API Fallback failed: {api_e}")
            
            # --- ENTERPRISE UPGRADE: Mixed Reviews (Real + Synthetic) ---
            url_lower = url.lower()
            if 'flipkart' in url_lower: platform = "Flipkart"
            elif 'myntra' in url_lower: platform = "Myntra"
            elif 'meesho' in url_lower: platform = "Meesho"
            elif 'ajio' in url_lower: platform = "Ajio"
            elif 'bigbasket' in url_lower or 'biggest' in url_lower: platform = "BigBasket"
            elif 'nykaa' in url_lower: platform = "Nykaa"
            elif 'shopsy' in url_lower: platform = "Shopsy"
            else: platform = "Amazon"
            if reviews:
                 print(f"Scraped {len(reviews)} real reviews. Adding synthetic ones...")
                 # Add a few synthetic ones but respect total max_items if possible
                 synth_count = max(1, min(5, max_items - len(reviews))) if max_items > len(reviews) else 0
                 mixed_reviews = generate_synthetic_reviews(reviews, platform=platform, count=synth_count)
                 return jsonify({'reviews': mixed_reviews, 'count': len(mixed_reviews), 'csv_saved': save_csv(mixed_reviews)})
            else:
                 print(f"Applying full mock fallback reviews for {platform} demonstration (count={max_items})...")
                 mixed_reviews = generate_synthetic_reviews([], platform=platform, count=max_items)
                 return jsonify({'reviews': mixed_reviews, 'count': len(mixed_reviews), 'csv_saved': save_csv(mixed_reviews)})

        except Exception as e:
             import traceback
             traceback.print_exc()
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
