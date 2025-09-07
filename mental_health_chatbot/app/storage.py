# app/storage.py
from __future__ import annotations
import os, sqlite3
from contextlib import contextmanager
from typing import Iterable, Any

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "mhc.db")

def init_db():
    schema_path = os.path.join(os.path.dirname(__file__), "..", "data", "schema.sql")
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        with open(schema_path, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()

@contextmanager
def conn_cursor():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        try:
            yield cur
            conn.commit()
        finally:
            cur.close()

def upsert_user(user_id: str, display_name: str | None = None):
    init_db()
    with conn_cursor() as cur:
        cur.execute(
            "INSERT INTO users (user_id, display_name) VALUES (?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET display_name=COALESCE(?, display_name)",
            (user_id, display_name, display_name),
        )

def log_chat(user_id: str, role: str, content: str):
    with conn_cursor() as cur:
        cur.execute(
            "INSERT INTO chat_logs (user_id, role, content) VALUES (?, ?, ?)",
            (user_id, role, content),
        )

def log_mood(user_id: str, date: str, mood: int, note: str | None):
    with conn_cursor() as cur:
        cur.execute(
            "INSERT OR REPLACE INTO mood_logs (user_id, date, mood, note) VALUES (?, ?, ?, ?)",
            (user_id, date, mood, note),
        )

def fetch_mood_series(user_id: str, limit_days: int = 14):
    with conn_cursor() as cur:
        cur.execute(
            "SELECT date, mood FROM mood_logs WHERE user_id = ? ORDER BY date DESC LIMIT ?",
            (user_id, limit_days),
        )
        rows = cur.fetchall()
    # reverse chronological → chronological
    rows = list(reversed(rows))
    return [(r["date"], r["mood"]) for r in rows]
