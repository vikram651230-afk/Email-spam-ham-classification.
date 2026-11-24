# Lifecycle stage 6 — Model Training
 
from pathlib import Path
import sys

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pandas as pd
import joblib
 
from sklearn.model_selection import train_test_split
from src.models.build_model import build_model
 
 
df = pd.read_csv(project_root / "data" / "processed" / "cleaned_emails.csv")
df["clean_email"] = df["clean_email"].fillna("")
 
# Load the vectorizer prepared in Stage 4 — transform only, never re-fit.
vectorizer = joblib.load(project_root / "models" / "count_vectorizer.pkl")
 
X = vectorizer.transform(df["clean_email"])
y = df["label"]
 
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)
 
# Build the untrained model from Stage 5, then fit it here.
model = build_model()
 
model.fit(X_train, y_train)
 
joblib.dump(model, project_root / "models" / "spam_model.pkl")
 
print("Training Completed")
