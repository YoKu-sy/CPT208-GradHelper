import json
import os
from typing import Any

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


load_dotenv()


RAGFLOW_BASE_URL = os.getenv("RAGFLOW_BASE_URL", "").rstrip("/")
RAGFLOW_API_KEY = os.getenv("RAGFLOW_API_KEY", "")
RAGFLOW_CHAT_ID = os.getenv("RAGFLOW_CHAT_ID", "").strip()
RAGFLOW_CHAT_NAME = os.getenv("RAGFLOW_CHAT_NAME", "").strip()
REQUEST_TIMEOUT = 120


app = FastAPI(title="RAGFlow Chat Proxy")
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
_chat_id_cache: str | None = None


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User question")
    session_id: str | None = Field(default=None, description="Existing RAGFlow session ID")
    session_name: str | None = Field(default=None, description="Optional session name for new sessions")


class ChatResponse(BaseModel):
    reply: str
    session_id: str | None = None
    reference: dict[str, Any] | list[Any] | None = None


def normalize_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
    if not text:
        return text

    # Recover common mojibake caused by UTF-8 bytes decoded as Latin-1/cp1252.
    if any(0x80 <= ord(ch) <= 0xFF for ch in text):
        try:
            repaired = text.encode("latin1").decode("utf-8")
            if repaired:
                return repaired.strip()
        except UnicodeError:
            pass
    return text


def ragflow_headers() -> dict[str, str]:
    if not RAGFLOW_BASE_URL or not RAGFLOW_API_KEY:
        raise HTTPException(status_code=500, detail="Missing RAGFlow configuration")
    return {"Authorization": f"Bearer {RAGFLOW_API_KEY}"}


def post_json(url: str, payload: dict[str, Any]) -> requests.Response:
    # This RAGFlow instance is more stable when the JSON body is ASCII-escaped.
    body = json.dumps(payload, ensure_ascii=True).encode("utf-8")
    return requests.post(
        url,
        headers={**ragflow_headers(), "Content-Type": "application/json; charset=utf-8"},
        data=body,
        timeout=REQUEST_TIMEOUT,
    )


def get_chat_id() -> str:
    global _chat_id_cache
    if _chat_id_cache:
        return _chat_id_cache
    if RAGFLOW_CHAT_ID:
        _chat_id_cache = RAGFLOW_CHAT_ID
        return _chat_id_cache
    if not RAGFLOW_CHAT_NAME:
        raise HTTPException(status_code=500, detail="Set RAGFLOW_CHAT_NAME or RAGFLOW_CHAT_ID")

    matches: list[dict[str, Any]] = []
    page = 1
    page_size = 100

    while True:
        response = requests.get(
            f"{RAGFLOW_BASE_URL}/api/v1/chats",
            params={"page": page, "page_size": page_size},
            headers=ragflow_headers(),
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()

        payload = response.json()
        data = payload.get("data") or {}
        chats = data.get("chats", [])
        matches.extend(chat for chat in chats if chat.get("name") == RAGFLOW_CHAT_NAME)

        total = data.get("total", 0)
        if page * page_size >= total or not chats:
            break
        page += 1

    if len(matches) == 1:
        _chat_id_cache = matches[0]["id"]
        return _chat_id_cache
    if len(matches) > 1:
        raise HTTPException(
            status_code=409,
            detail=f"Multiple chats found with name '{RAGFLOW_CHAT_NAME}'. Set RAGFLOW_CHAT_ID explicitly.",
        )

    raise HTTPException(status_code=404, detail=f"Chat '{RAGFLOW_CHAT_NAME}' not found")


def create_session(chat_id: str, session_name: str | None = None) -> str:
    payload: dict[str, Any] = {}
    if session_name:
        payload["name"] = session_name

    response = post_json(f"{RAGFLOW_BASE_URL}/api/v1/chats/{chat_id}/sessions", payload)
    response.raise_for_status()

    data = response.json()
    if data.get("code") != 0:
        raise HTTPException(status_code=502, detail=data.get("message") or "Failed to create session")

    session_id = (data.get("data") or {}).get("id")
    if not session_id:
        raise HTTPException(status_code=502, detail="RAGFlow did not return a session_id")
    return session_id


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    chat_id = get_chat_id()
    question = normalize_text(request.question)
    session_name = normalize_text(request.session_name)
    session_id = request.session_id or create_session(chat_id, session_name)

    response = post_json(
        f"{RAGFLOW_BASE_URL}/api/v1/chats/{chat_id}/completions",
        {"question": question, "stream": False, "session_id": session_id},
    )
    response.raise_for_status()

    payload = response.json()
    if payload.get("code") != 0:
        raise HTTPException(status_code=502, detail=payload.get("message") or "RAGFlow request failed")

    data = payload.get("data") or {}
    return ChatResponse(
        reply=normalize_text(data.get("answer", "")) or "",
        session_id=data.get("session_id") or session_id,
        reference=data.get("reference"),
    )
