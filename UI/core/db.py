# UI/core/db.py
from __future__ import annotations


import sqlite3
from pathlib import Path
from typing import List, Dict, Optional

from .config import settings


def _get_conn() -> sqlite3.Connection:
    db_path = Path(settings.SQLITE_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = _get_conn()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


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




def start_embedding_run(model_id: str, device: str, collection: str, chroma_dir: str) -> int:
    conn = _get_conn()
    conn.execute(
        """
        INSERT INTO embedding_runs(started_at, status, model_id, device, collection, chroma_dir)
        VALUES(?, 'running', ?, ?, ?, ?)
        """,
        (time.time(), model_id, device, collection, chroma_dir),
    )
    conn.commit()
    return int(conn.lastrowid)

def finish_embedding_run(
        

    run_id: int,
    status: str,

    note: str = "",

    total_rows: Optional[int] = None,
    total_chunks: Optional[int] = None) -> None:
        conn = _get_conn()
        conn.execute(
                """
                UPDATE embedding_runs
                SET finished_at=?, status=?, note=?, total_rows=?, total_chunks=?
                WHERE id=?
                """,
                (time.time(), status, note, total_rows, total_chunks, run_id),
            )                                        
        conn.commit()


def get_embedding_logs(limit: int = 30) -> List[Dict[str, Any]]:
    conn = _get_conn()
    rows = conn.execute(
            "SELECT * FROM embedding_runs ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]

