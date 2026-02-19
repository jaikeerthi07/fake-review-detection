import pandas as pd
from textblob import TextBlob

df = pd.read_csv(r'd:\fake review detection\uploads\fake_review_dataset.csv')
text_col = 'review_text'

# Sample polarity values
polarities = df[text_col].head(200).apply(lambda t: TextBlob(str(t)).sentiment.polarity)
print("Polarity stats:")
print(polarities.describe())
print("\nDistribution:")
print(f"< -0.3 (1 star): {(polarities < -0.3).sum()}")
print(f"-0.3 to -0.05 (2 star): {((polarities >= -0.3) & (polarities < -0.05)).sum()}")
print(f"-0.05 to 0.1 (3 star): {((polarities >= -0.05) & (polarities < 0.1)).sum()}")
print(f"0.1 to 0.4 (4 star): {((polarities >= 0.1) & (polarities < 0.4)).sum()}")
print(f">= 0.4 (5 star): {(polarities >= 0.4).sum()}")
