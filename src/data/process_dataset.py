# Lifecycle stage 4 - Data Preparation (full dataset)
 
from pathlib import Path

from src.data.load_data import load_data
from src.data.preprocess import clean_batch
 
def process_dataset():
 
    print("Script Started")
 
    project_root = Path(__file__).resolve().parents[2]
    input_path = project_root / "data" / "raw" / "email_spam.csv"
    output_path = project_root / "data" / "processed" / "cleaned_emails.csv"

    df = load_data(input_path)
 
    print("Dataset Loaded")
 
    # Lowercasing + regex are fast as vectorized pandas operations,
    # so we do them here and leave only tokenizing/lemmatizing to spaCy.
 
    texts = df["text"].astype(str).str.lower()
    texts = texts.str.replace(r"http\S+", "", regex=True)
    texts = texts.str.replace(r"[^a-zA-Z ]", "", regex=True)
 
    df["clean_email"] = clean_batch(texts)
 
    print("Cleaning Completed")
 
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
 
    print("File Saved")

    print(df["label"].value_counts())