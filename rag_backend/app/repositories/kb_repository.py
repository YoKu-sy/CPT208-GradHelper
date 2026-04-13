import json
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any

from app.core.config import get_settings


class KnowledgeBaseRepository:
    def __init__(self, db_path: str | None = None) -> None:
        settings = get_settings()
        self._db_path = Path(db_path or settings.metadata_db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @property
    def db_path(self) -> Path:
        return self._db_path

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with closing(self._connect()) as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT   EXISTS datasets (
                    dataset_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    embedding_model TEXT,
                    chunk_method TEXT,
                    document_count INTEGER DEFAULT 0,
                    chunk_count INTEGER DEFAULT 0,
                    raw_json TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS documents (
                    document_id TEXT PRIMARY KEY,
                    dataset_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    chunk_method TEXT,
                    source_type TEXT,
                    size INTEGER DEFAULT 0,
                    token_count INTEGER DEFAULT 0,
                    chunk_count INTEGER DEFAULT 0,
                    run TEXT,
                    status TEXT,
                    parse_status TEXT DEFAULT 'UNSTART',
                    progress REAL DEFAULT 0,
                    progress_message TEXT DEFAULT '',
                    raw_json TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(dataset_id) REFERENCES datasets(dataset_id)
                );
                """
            )
            columns = {
                row["name"]
                for row in connection.execute("PRAGMA table_info(documents)").fetchall()
            }
            if "progress_message" not in columns:
                connection.execute("ALTER TABLE documents ADD COLUMN progress_message TEXT DEFAULT ''")
            if "parse_status" not in columns:
                connection.execute("ALTER TABLE documents ADD COLUMN parse_status TEXT DEFAULT 'UNSTART'")
            connection.commit()

    def upsert_dataset(self, dataset_data: dict[str, Any]) -> None:
        with closing(self._connect()) as connection:
            connection.execute(
                """
                INSERT INTO datasets (
                    dataset_id, name, embedding_model, chunk_method,
                    document_count, chunk_count, raw_json, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(dataset_id) DO UPDATE SET
                    name=excluded.name,
                    embedding_model=excluded.embedding_model,
                    chunk_method=excluded.chunk_method,
                    document_count=excluded.document_count,
                    chunk_count=excluded.chunk_count,
                    raw_json=excluded.raw_json,
                    updated_at=CURRENT_TIMESTAMP
                """,
                (
                    dataset_data["dataset_id"],
                    dataset_data["name"],
                    dataset_data.get("embedding_model"),
                    dataset_data.get("chunk_method"),
                    dataset_data.get("document_count", 0),
                    dataset_data.get("chunk_count", 0),
                    json.dumps(dataset_data, ensure_ascii=True),
                ),
            )
            connection.commit()

    def upsert_document(self, document_data: dict[str, Any]) -> None:
        with closing(self._connect()) as connection:
            connection.execute(
                """
                INSERT INTO documents (
                    document_id, dataset_id, name, chunk_method, source_type, size,
                    token_count, chunk_count, run, status, parse_status, progress, progress_message, raw_json, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(document_id) DO UPDATE SET
                    dataset_id=excluded.dataset_id,
                    name=excluded.name,
                    chunk_method=excluded.chunk_method,
                    source_type=excluded.source_type,
                    size=excluded.size,
                    token_count=excluded.token_count,
                    chunk_count=excluded.chunk_count,
                    run=excluded.run,
                    status=excluded.status,
                    parse_status=excluded.parse_status,
                    progress=excluded.progress,
                    progress_message=excluded.progress_message,
                    raw_json=excluded.raw_json,
                    updated_at=CURRENT_TIMESTAMP
                """,
                (
                    document_data["document_id"],
                    document_data["dataset_id"],
                    document_data["name"],
                    document_data.get("chunk_method"),
                    document_data.get("source_type"),
                    document_data.get("size", 0),
                    document_data.get("token_count", 0),
                    document_data.get("chunk_count", 0),
                    document_data.get("run"),
                    document_data.get("status"),
                    document_data.get("parse_status", "UNSTART"),
                    document_data.get("progress", 0),
                    document_data.get("progress_message", ""),
                    json.dumps(document_data, ensure_ascii=True),
                ),
            )
            connection.commit()

    def get_document(self, document_id: str) -> dict[str, Any] | None:
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT * FROM documents WHERE document_id = ?",
                (document_id,),
            ).fetchone()
        return dict(row) if row else None

    def get_documents(self, document_ids: list[str]) -> list[dict[str, Any]]:
        if not document_ids:
            return []

        placeholders = ",".join("?" for _ in document_ids)
        with closing(self._connect()) as connection:
            rows = connection.execute(
                f"SELECT * FROM documents WHERE document_id IN ({placeholders})",
                tuple(document_ids),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_documents_by_dataset(self, dataset_id: str) -> list[dict[str, Any]]:
        with closing(self._connect()) as connection:
            rows = connection.execute(
                "SELECT * FROM documents WHERE dataset_id = ? ORDER BY created_at DESC",
                (dataset_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_dataset(self, dataset_id: str) -> dict[str, Any] | None:
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT * FROM datasets WHERE dataset_id = ?",
                (dataset_id,),
            ).fetchone()
        return dict(row) if row else None

    def get_datasets(self, dataset_ids: list[str]) -> list[dict[str, Any]]:
        if not dataset_ids:
            return []

        placeholders = ",".join("?" for _ in dataset_ids)
        with closing(self._connect()) as connection:
            rows = connection.execute(
                f"SELECT * FROM datasets WHERE dataset_id IN ({placeholders})",
                tuple(dataset_ids),
            ).fetchall()
        return [dict(row) for row in rows]
