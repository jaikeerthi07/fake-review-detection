from app import app, db, Review
from datetime import datetime

with app.app_context():
    db.create_all()
    count = Review.query.count()
    print(f"Current review count: {count}")
    
    if count == 0:
        print("Seeding database...")
        initial_data = [
            {'text': 'Absolutely love this product! It works perfectly.', 'label': 'Genuine', 'confidence': 0.98, 'sentiment': 0.85, 'time': '10:15:23', 'date': '2026-02-14'},
            {'text': 'Total scam. Do not buy. Waste of money.', 'label': 'Fake', 'confidence': 0.95, 'sentiment': -0.80, 'time': '10:18:45', 'date': '2026-02-14'},
            {'text': 'Arrived on time and packaging was good.', 'label': 'Genuine', 'confidence': 0.92, 'sentiment': 0.60, 'time': '10:22:10', 'date': '2026-02-15'},
            {'text': 'Best ever! Highly recommend! Wow!', 'label': 'Fake', 'confidence': 0.89, 'sentiment': 0.95, 'time': '10:30:00', 'date': '2026-02-15'},
            {'text': 'Example of a normal review for testing.', 'label': 'Genuine', 'confidence': 0.85, 'sentiment': 0.10, 'time': '10:35:12', 'date': '2026-02-16'}
        ]
        for item in initial_data:
            dt_str = f"{item['date']} {item['time']}"
            dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            review = Review(text=item['text'], label=item['label'], confidence=float(item['confidence']), sentiment=item['sentiment'], timestamp=dt)
            db.session.add(review)
        db.session.commit()
        print("Seeding complete.")
    else:
        print("Database already has data.")
