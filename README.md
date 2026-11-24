<<<<<<< HEAD
# 🛡️ Spam Shield — Email Spam / Ham Classification (End-to-End Deployment)

An end-to-end machine learning project that classifies emails/SMS messages as **spam** or **ham** (legitimate), served through a **FastAPI** web application with a modern UI.

![Python](https://img.shields.io/badge/Python-3.11-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-009688) ![scikit-learn](https://img.shields.io/badge/scikit--learn-Naive%20Bayes-orange) ![spaCy](https://img.shields.io/badge/spaCy-NLP-09a3d5)

---

## 📌 Table of Contents
1. [Business Understanding](#-business-understanding)
2. [Project Lifecycle](#-project-lifecycle)
3. [Tech Stack](#-tech-stack)
4. [Project Structure](#-project-structure)
5. [Model Performance](#-model-performance)
6. [Web Application Features](#-web-application-features)
7. [Getting Started](#-getting-started)
8. [API Reference](#-api-reference)
9. [Retraining the Model](#-retraining-the-model)
10. [Future Improvements](#-future-improvements)

---

## 💼 Business Understanding

Spam emails waste time, spread phishing and scams, and put users and organisations at financial and security risk. At the same time, a **false positive** (a genuine email wrongly marked as spam) can mean a missed invoice, job offer, or customer request.

**Goal:** automatically detect spam with high accuracy while keeping false alarms on legitimate email as low as possible, and make the model easy to use through a web interface and a REST API.

**Success criteria**
- High overall accuracy and spam recall.
- Very few legitimate emails flagged as spam.
- Real-time predictions through an easy-to-use application.

---

## 🔁 Project Lifecycle

| Stage | Description | Script |
|---|---|---|
| 3 – Data Understanding | Load raw dataset and standardise columns | `src/data/load_data.py` |
| 4 – Data Preparation | Lowercase, remove URLs/special characters, remove stop-words, lemmatise (spaCy) | `src/data/preprocess.py`, `src/data/process_dataset.py` |
| 4 – Feature Extraction | Bag-of-words `CountVectorizer` (1–2 grams, 5000 features) | `src/features/vectorizer.py` |
| 5 – Model Building | Multinomial Naive Bayes (Laplace smoothing α = 1.0) | `src/models/build_model.py` |
| 6 – Model Training | 80/20 stratified split, fit and save model | `src/models/train.py` |
| 7 – Model Testing | Interactive command-line predictions | `src/models/predict.py` |
| 8 – Model Evaluation | Classification report and confusion matrix | `src/models/evaluate.py` |
| 9 – Deployment | FastAPI application and web UI | `app/` |

---

## 🧰 Tech Stack

- **Language:** Python 3.11
- **NLP:** spaCy (`en_core_web_sm`), regex
- **ML:** scikit-learn (CountVectorizer + MultinomialNB), joblib
- **Backend:** FastAPI, Uvicorn, Jinja2
- **Frontend:** HTML, CSS, vanilla JavaScript (no build step)
- **Data:** pandas, numpy

---

## 📂 Project Structure

```
Project 02 Email Spam-Ham Classification E2E Deployment/
│
├── app/                         # FastAPI web application
│   ├── main.py                  # API routes and app startup
│   ├── services.py              # Model loading, prediction, insights
│   ├── templates/index.html     # UI page
│   └── static/                  # style.css, app.js
│
├── src/
│   ├── data/                    # load_data, preprocess, process_dataset
│   ├── features/                # vectorizer
│   └── models/                  # build_model, train, evaluate, predict
│
├── data/
│   ├── raw/email_spam.csv       # original dataset
│   └── processed/cleaned_emails.csv
│
├── models/
│   ├── count_vectorizer.pkl
│   └── spam_model.pkl
│
├── main.py                      # runs the data-cleaning pipeline
├── requirements.txt
└── README.md
```

---

## 📊 Model Performance

Evaluated on a stratified 20% hold-out test set (1,115 messages):

| Metric | Score |
|---|---|
| Accuracy | **98.2%** |
| Spam precision | 96.4% |
| Spam recall | 89.9% |

**Confusion matrix**

|  | Predicted spam | Predicted ham |
|---|---|---|
| **Actual spam** | 134 | 15 |
| **Actual ham** | 5 | 961 |

Run `python src/models/evaluate.py` to reproduce the full report.

---

## ✨ Web Application Features

- **Check Email** – paste a message and get an instant verdict, spam-probability meter, and the words that influenced the decision.
- **Batch Scan** – classify up to 200 messages from pasted lines or an uploaded `.txt` / `.csv` file.
- **Model Insights** – accuracy, precision, recall, F1, confusion matrix, dataset stats, and the strongest spam/ham words.
- Responsive layout with automatic light/dark mode.

> 📸 Add screenshots here, e.g. `![Home](docs/home.png)`

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>
```

### 2. Create and activate a virtual environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 4. Run the web app
```bash
uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000** in your browser. Interactive API docs are at **http://127.0.0.1:8000/docs**.

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Web UI |
| GET | `/api/health` | Health check |
| POST | `/api/predict` | Classify a single email |
| POST | `/api/predict-batch` | Classify a list of emails (max 200) |
| POST | `/api/predict-file` | Classify emails from an uploaded `.txt` / `.csv` |
| GET | `/api/insights` | Model metrics and top words |

**Example**
```bash
curl -X POST http://127.0.0.1:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "WINNER!! Claim your free prize now"}'
```
```json
{
  "label": "spam",
  "spam_probability": 1.0,
  "confidence": 1.0,
  "known_terms": 5,
  "spam_signals": ["claim", "prize", "winner", "claim free", "free"],
  "ham_signals": []
}
```

---

## 🔄 Retraining the Model

Trained models are already included. To rebuild from scratch (run from the project root):

```bash
python main.py                       # clean the raw dataset
python src/features/vectorizer.py    # build the vectorizer
python src/models/train.py           # train and save the model
python src/models/evaluate.py        # evaluate
python src/models/predict.py         # optional: CLI testing
```

---

## 🔮 Future Improvements

- Try TF-IDF, Logistic Regression, SVM, or transformer models and compare.
- Tune the decision threshold to trade recall against false alarms.
- Dockerise and deploy to a cloud platform.
- Add automated tests and CI with GitHub Actions.

---

## 📄 License

Released under the MIT License — see `LICENSE` (add one if you want others to reuse the project).

# Spam Shield – FastAPI Web App

## Run locally (VS Code terminal, from the project root)
```
python -m venv .venv
.venv\Scripts\activate            # Windows   (mac/linux: source .venv/bin/activate)
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000  (API docs: http://127.0.0.1:8000/docs)

## Endpoints
| Method | Path | Purpose |
|---|---|---|
| GET | `/` | Web UI |
| GET | `/api/health` | Health check |
| POST | `/api/predict` | `{"text": "..."}` -> label, probability, signal words |
| POST | `/api/predict-batch` | `{"emails": [...]}` (max 200) |
| POST | `/api/predict-file` | Upload .txt / .csv |
| GET | `/api/insights` | Accuracy, confusion matrix, top words |

## Re-train (optional; models are already included)
```
python main.py                    # clean data
python src/features/vectorizer.py
python src/models/train.py
python src/models/evaluate.py
```
=======
# Email-spam-ham-classification.
>>>>>>> a5fc6e5e39349798770dc053f503e954e7c7173c
