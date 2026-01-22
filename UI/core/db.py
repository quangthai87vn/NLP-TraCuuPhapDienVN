# UI/core/db.py
from __future__ import annotations

import sqlite3
import time
from pathlib import Path
from typing import Dict, List, Optional

from .config import settings


def _get_conn() -> sqlite3.Connection:
    db_path = Path(settings.SQLITE_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return {r["name"] for r in rows}


def _ensure_columns(conn: sqlite3.Connection, table: str, columns_sql: List[str]) -> None:
    # columns_sql: ["col_name TYPE DEFAULT ...", ...]
    existing = _table_columns(conn, table)
    for col in columns_sql:
        col_name = col.split()[0].strip()
        if col_name not in existing:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {col}")


def init_db() -> None:
    """Gọi 1 lần khi app start (hoặc gọi ở mỗi page cũng ok)."""
    conn = _get_conn()
    try:
        # Chat history
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at REAL DEFAULT (strftime('%s','now'))
            )
            """
        )

        # Embedding logs
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS embedding_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                started_at REAL NOT NULL,
                finished_at REAL,
                status TEXT NOT NULL,
                note TEXT DEFAULT '',
                model_id TEXT,
                device TEXT,
                collection TEXT,
                chroma_dir TEXT,
                total_rows INTEGER,
                total_chunks INTEGER
            )
            """
        )

        # Nếu table đã tồn tại từ trước nhưng thiếu cột -> migrate nhẹ
        _ensure_columns(
            conn,
            "embedding_runs",
            [
                "finished_at REAL",
                "status TEXT",
                "note TEXT DEFAULT ''",
                "model_id TEXT",
                "device TEXT",
                "collection TEXT",
                "chroma_dir TEXT",
                "total_rows INTEGER",
                "total_chunks INTEGER",
            ],
        )

        conn.commit()
    finally:
        conn.close()


# -----------------------
# Chat messages
# -----------------------
def add_chat_message(role: str, content: str) -> None:
    conn = _get_conn()
    try:
        conn.execute(
            "INSERT INTO chat_messages(role, content) VALUES(?, ?)",
            (role, content),
        )
        conn.commit()
    finally:
        conn.close()


def get_chat_messages(limit: int = 200) -> List[Dict]:
    conn = _get_conn()
    try:
        rows = conn.execute(
            "SELECT role, content, created_at FROM chat_messages ORDER BY id ASC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def clear_chat_messages() -> None:
    conn = _get_conn()
    try:
        conn.execute("DELETE FROM chat_messages")
        conn.commit()
    finally:
        conn.close()


# -----------------------
# Embedding runs
# -----------------------
def start_embedding_run(model_id: str, device: str, collection: str, chroma_dir: str) -> int:
    init_db()  # đảm bảo table tồn tại
    conn = _get_conn()
    try:
        cur = conn.execute(
            """
            INSERT INTO embedding_runs(started_at, status, note, model_id, device, collection, chroma_dir)
            VALUES(?, 'running', '', ?, ?, ?, ?)
            """,
            (time.time(), model_id, device, collection, chroma_dir),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def finish_embedding_run(
    run_id: int,
    status: str,
    note: str = "",
    total_rows: Optional[int] = None,
    total_chunks: Optional[int] = None,
) -> None:
    init_db()
    conn = _get_conn()
    try:
        conn.execute(
            """
            UPDATE embedding_runs
            SET finished_at=?, status=?, note=?, total_rows=COALESCE(?, total_rows),
                total_chunks=COALESCE(?, total_chunks)
            WHERE id=?
            """,
            (time.time(), status, note, total_rows, total_chunks, run_id),
        )
        conn.commit()
    finally:
        conn.close()


def get_embedding_logs(limit: int = 20) -> List[Dict]:
    init_db()
    conn = _get_conn()
    try:
        rows = conn.execute(
            """
            SELECT id, started_at, finished_at, status, note,
                   model_id, device, collection, chroma_dir, total_rows, total_chunks
            FROM embedding_runs
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
