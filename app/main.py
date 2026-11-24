"""FastAPI web application for Email Spam / Ham classification.

Run from the project root:
    uvicorn app.main:app --reload
Then open http://127.0.0.1:8000
"""
import csv
import io
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from app.services import SpamService

BASE = Path(__file__).resolve().parent
MAX_BATCH = 200


class EmailIn(BaseModel):
    text: str = Field(..., min_length=1, max_length=20000)


class BatchIn(BaseModel):
    emails: list[str] = Field(..., min_length=1, max_length=MAX_BATCH)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.svc = SpamService()      # load model once at startup
    yield


app = FastAPI(title="Spam Shield - Email Spam/Ham Classifier", version="1.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
templates = Jinja2Templates(directory=BASE / "templates")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/api/health")
async def health():
    return {"status": "ok", "model": "MultinomialNB", "classes": app.state.svc.classes}


@app.post("/api/predict")
async def predict(payload: EmailIn):
    if not payload.text.strip():
        raise HTTPException(422, "Email text is empty.")
    return app.state.svc.predict(payload.text)


@app.post("/api/predict-batch")
async def predict_batch(payload: BatchIn):
    return _batch(payload.emails)


@app.post("/api/predict-file")
async def predict_file(file: UploadFile = File(...)):
    """Accepts .txt (one email per line) or .csv (uses a 'text'/'v2'/'message' column, else first column)."""
    raw = (await file.read()).decode("utf-8", errors="ignore")
    if (file.filename or "").lower().endswith(".csv"):
        rows = list(csv.reader(io.StringIO(raw)))
        if not rows:
            raise HTTPException(422, "Empty file.")
        header = [h.strip().lower() for h in rows[0]]
        col = next((header.index(c) for c in ("text", "v2", "message", "email", "body") if c in header), None)
        data = rows[1:] if col is not None else rows
        emails = [r[col or 0] for r in data if r and len(r) > (col or 0)]
    else:
        emails = raw.splitlines()
    emails = [e for e in (x.strip() for x in emails) if e][:MAX_BATCH]
    if not emails:
        raise HTTPException(422, "No emails found in file.")
    return _batch(emails)


def _batch(emails: list[str]) -> dict:
    svc = app.state.svc
    results = []
    for e in emails:
        r = svc.predict(e)
        r["preview"] = e[:140] + ("…" if len(e) > 140 else "")
        results.append(r)
    spam = sum(r["label"] == "spam" for r in results)
    return {"total": len(results), "spam": spam, "ham": len(results) - spam, "results": results}


@app.get("/api/insights")
async def insights():
    return app.state.svc.insights()
