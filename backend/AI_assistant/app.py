import random
import re
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "assistant.db"

app = FastAPI(title="AI Assistant Similar Offer API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ProfileRequest(BaseModel):
    major: str = Field(..., min_length=1)
    gpa: str = Field(..., min_length=1)
    additional_info: str = Field(default="")


class OfferItem(BaseModel):
    major: str | None = None
    offer: str | None = None
    gpa: str | None = None
    status: str | None = None
    research: int | None = None
    internship: int | None = None
    additional_notes: str | None = None


class ProfileSearchResponse(BaseModel):
    results: list[OfferItem]
    count: int


_GPA_RE = re.compile(r"-?\d+(?:\.\d+)?")
_WORD_RE = re.compile(r"[A-Za-z0-9]+")


STOPWORDS = {
    "the",
    "and",
    "or",
    "of",
    "to",
    "a",
    "an",
    "in",
    "for",
    "with",
    "on",
    "at",
    "by",
    "from",
    "my",
    "me",
    "i",
    "we",
    "our",
    "you",
    "your",
    "is",
    "are",
    "was",
    "were",
    "this",
    "that",
    "it",
    "as",
    "be",
    "been",
    "have",
    "has",
    "had",
    "but",
    "not",
    "very",
    "more",
    "most",
    "less",
    "less",
}


def parse_gpa(raw: str) -> float:
    match = _GPA_RE.search(raw)
    if not match:
        raise HTTPException(status_code=400, detail="Invalid gpa format")
    return float(match.group(0))


def get_connection() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise HTTPException(status_code=500, detail="Database not found")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def tokenize(text: str) -> list[str]:
    tokens = [token.lower() for token in _WORD_RE.findall(text)]
    return [token for token in tokens if token not in STOPWORDS and len(token) > 1]


def similarity_score(query_text: str, candidate_text: str) -> int:
    query_tokens = tokenize(query_text)
    candidate_tokens = tokenize(candidate_text)
    if not query_tokens or not candidate_tokens:
        return 0

    query_counts = Counter(query_tokens)
    candidate_counts = Counter(candidate_tokens)
    return sum(min(query_counts[token], candidate_counts[token]) for token in query_counts.keys() & candidate_counts.keys())


@app.post("/profile/search", response_model=ProfileSearchResponse)
def search_profiles(payload: ProfileRequest) -> ProfileSearchResponse:
    target_gpa = parse_gpa(payload.gpa)
    major = payload.major.strip()
    extra = payload.additional_info.strip()

    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT major, offer, gpa, status, research, internship, additional_notes
            FROM offers
            WHERE major = ?
              AND ABS(CAST(gpa AS REAL) - ?) <= 0.4
            """,
            (major, target_gpa),
        ).fetchall()
    finally:
        conn.close()

    results = [dict(row) for row in rows]
    scored_results = []
    for item in results:
        candidate_text = " ".join(
            str(value or "")
            for value in (
                item.get("major"),
                item.get("offer"),
                item.get("status"),
                item.get("additional_notes"),
            )
        )
        match_score = similarity_score(extra, candidate_text) if extra else 0
        scored_results.append((match_score, random.random(), item))

    scored_results.sort(key=lambda row: (-row[0], row[1]))
    top_results = [item for _, _, item in scored_results[:50]]

    return ProfileSearchResponse(
        results=[OfferItem(**item) for item in top_results],
        count=len(top_results),
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
