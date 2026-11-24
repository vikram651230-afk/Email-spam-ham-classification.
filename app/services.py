"""Model service: loads the trained artifacts once and exposes predict / insights.

Re-uses the project's own pipeline (src.data.preprocess.clean_text) so that
web predictions are processed exactly like the training data.
"""
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support
from sklearn.model_selection import train_test_split

from src.data.preprocess import clean_text

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "spam_model.pkl"
VECTORIZER_PATH = ROOT / "models" / "count_vectorizer.pkl"
DATA_PATH = ROOT / "data" / "processed" / "cleaned_emails.csv"


class SpamService:
    def __init__(self):
        self.model = joblib.load(MODEL_PATH)
        self.vectorizer = joblib.load(VECTORIZER_PATH)
        self.classes = list(self.model.classes_)
        self.spam_idx = self.classes.index("spam")
        self.vocab = np.array(self.vectorizer.get_feature_names_out())
        self._insights = None

    # ---------- prediction ----------
    def _explain(self, X, k=6):
        """Words in this message that push the model most towards spam / ham."""
        idx = X.nonzero()[1]
        if len(idx) == 0:
            return [], []
        lp = self.model.feature_log_prob_
        score = lp[self.spam_idx, idx] - lp[1 - self.spam_idx, idx]  # >0 => spam-leaning
        order = np.argsort(score)
        spam_words = [self.vocab[idx[i]] for i in order[::-1][:k] if score[i] > 0]
        ham_words = [self.vocab[idx[i]] for i in order[:k] if score[i] < 0]
        return spam_words, ham_words

    def predict(self, text: str) -> dict:
        cleaned = clean_text(text)
        X = self.vectorizer.transform([cleaned])
        proba = self.model.predict_proba(X)[0]
        spam_p = float(proba[self.spam_idx])
        label = "spam" if spam_p >= 0.5 else "ham"
        confidence = spam_p if label == "spam" else 1 - spam_p
        spam_words, ham_words = self._explain(X)
        return {
            "label": label,
            "spam_probability": round(spam_p, 4),
            "confidence": round(confidence, 4),
            "known_terms": int(X.nnz),
            "spam_signals": spam_words,
            "ham_signals": ham_words,
        }

    # ---------- model insights ----------
    def insights(self) -> dict:
        if self._insights is not None:
            return self._insights
        df = pd.read_csv(DATA_PATH)
        df["clean_email"] = df["clean_email"].fillna("")
        X = self.vectorizer.transform(df["clean_email"])
        y = df["label"]
        _, X_te, _, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        pred = self.model.predict(X_te)
        p, r, f, _ = precision_recall_fscore_support(y_te, pred, labels=["spam"], zero_division=0)
        cm = confusion_matrix(y_te, pred, labels=["spam", "ham"])
        lp = self.model.feature_log_prob_
        diff = lp[self.spam_idx] - lp[1 - self.spam_idx]
        top_spam = np.argsort(diff)[::-1][:12]
        top_ham = np.argsort(diff)[:12]
        counts = y.value_counts()
        self._insights = {
            "dataset": {"total": int(len(df)), "spam": int(counts.get("spam", 0)), "ham": int(counts.get("ham", 0))},
            "test_size": int(len(y_te)),
            "accuracy": round(float(accuracy_score(y_te, pred)), 4),
            "spam_precision": round(float(p[0]), 4),
            "spam_recall": round(float(r[0]), 4),
            "spam_f1": round(float(f[0]), 4),
            "confusion_matrix": {
                "true_spam_pred_spam": int(cm[0][0]), "true_spam_pred_ham": int(cm[0][1]),
                "true_ham_pred_spam": int(cm[1][0]), "true_ham_pred_ham": int(cm[1][1]),
            },
            "top_spam_words": [self.vocab[i] for i in top_spam],
            "top_ham_words": [self.vocab[i] for i in top_ham],
            "algorithm": "Multinomial Naive Bayes",
            "features": "Bag-of-words (1-2 grams, 5000 features)",
        }
        return self._insights
