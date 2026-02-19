from fpdf import FPDF
from datetime import datetime
import os

class TrustLensReport(FPDF):
    def __init__(self, product_title, url):
        super().__init__()
        self.product_title = product_title
        self.url = url
        self.brand_color = (66, 133, 244) # Google Blue-ish
        self.secondary_color = (100, 100, 100)
        
    def header(self):
        # Logo placeholder (text for now)
        self.set_font('Arial', 'B', 20)
        self.set_text_color(*self.brand_color)
        self.cell(0, 10, 'TrustLens Audit Report', 0, 1, 'L')
        
        # Date
        self.set_font('Arial', 'I', 10)
        self.set_text_color(*self.secondary_color)
        self.cell(0, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'L')
        self.ln(5)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 14)
        self.set_text_color(0)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(2)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.set_text_color(50)
        self.multi_cell(0, 6, body)
        self.ln()

    def add_score_section(self, trust_score, review_count, real_count, fake_count):
        self.add_page()
        
        # Product Info
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, f"Product: {self.product_title[:80]}...", 0, 1)
        self.set_font('Arial', '', 10)
        self.cell(0, 10, f"URL: {self.url[:60]}...", 0, 1)
        self.ln(10)
        
        # Big Score
        self.set_font('Arial', 'B', 40)
        if trust_score > 70:
            self.set_text_color(0, 128, 0) # Green
        elif trust_score > 40:
             self.set_text_color(255, 165, 0) # Orange
        else:
             self.set_text_color(255, 0, 0) # Red
             
        self.cell(0, 20, f"{trust_score}% Trust Score", 0, 1, 'C')
        self.ln(10)
        
        # Stats Grid
        self.set_font('Arial', 'B', 12)
        self.set_text_color(0)
        
        self.cell(60, 10, f"Total Reviews: {review_count}", 1, 0, 'C')
        self.cell(60, 10, f"Real Reviews: {real_count}", 1, 0, 'C')
        self.cell(60, 10, f"Fake Reviews: {fake_count}", 1, 1, 'C')
        self.ln(10)

    def add_details_section(self, avg_rating, sentiment_score, top_keywords):
        self.chapter_title("Analysis Details")
        
        # Sentiment
        sent_text = "Positive" if sentiment_score > 0.2 else "Negative" if sentiment_score < -0.2 else "Neutral"
        self.chapter_body(f"Average Rating: {avg_rating} Stars")
        self.chapter_body(f"Overall Sentiment: {sent_text} ({sentiment_score:.2f})")
        self.ln(5)
        
        # Keywords
        if top_keywords:
            self.chapter_title("Key Indicators")
            self.chapter_body("Common terms found in reviews:")
            for k in top_keywords:
                self.cell(0, 8, f"- {k}", 0, 1)
            self.ln(5)

def generate_report(data, filename="report.pdf"):
    pdf = TrustLensReport(data.get('title', 'Unknown Product'), data.get('url', 'N/A'))
    
    # Calculate stats
    reviews = data.get('reviews', [])
    total = len(reviews)
    real = len([r for r in reviews if r.get('label') == 'Real' or r.get('label') == 'OR'])
    fake = total - real
    score = data.get('trust_score', 0)
    
    pdf.add_score_section(score, total, real, fake)
    
    avg_rating = sum([float(r.get('rating', 0) or 0) for r in reviews]) / total if total else 0
    avg_sentiment = sum([float(r.get('sentiment', 0) or 0) for r in reviews]) / total if total else 0
    
    pdf.add_details_section(avg_rating, avg_sentiment, data.get('keywords', []))
    
    output_path = os.path.join("uploads", filename)
    pdf.output(output_path)
    return output_path
