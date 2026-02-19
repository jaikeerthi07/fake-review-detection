from report_generator import TrustLensReport, generate_report
import os

print("Testing PDF Generation...")

dummy_data = {
    'title': 'Test Product for Entperprise Features',
    'url': 'https://example.com/product',
    'trust_score': 85.5,
    'reviews': [
        {'label': 'Real', 'rating': 5, 'sentiment': 0.8},
        {'label': 'Real', 'rating': 4, 'sentiment': 0.6},
        {'label': 'Fake', 'rating': 5, 'sentiment': 0.9},
        {'label': 'Real', 'rating': 5, 'sentiment': 0.7},
    ],
    'keywords': ['quality', 'shipping', 'value']
}

try:
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
        
    output = generate_report(dummy_data, "test_report.pdf")
    print(f"Report generated successfully at: {output}")
    print(f"File size: {os.path.getsize(output)} bytes")
except Exception as e:
    print(f"Error generating report: {e}")
    import traceback
    traceback.print_exc()
