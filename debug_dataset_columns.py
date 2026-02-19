import pandas as pd
import os

try:
    path = r'd:\fake review detection\uploads\fake_review_dataset.csv'
    if os.path.exists(path):
        df = pd.read_csv(path)
        print("Columns:", df.columns.tolist())
        print("Head:", df.head(1).to_dict())
    else:
        print("Dataset file not found at", path)
except Exception as e:
    print("Error reading dataset:", e)
