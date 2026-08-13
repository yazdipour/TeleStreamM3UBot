import os
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone

_SCHEMA = """
CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    message_id INTEGER,
    added_at TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1
);
"""


@dataclass
class Entry:
    id: int
    url: str
    title: str
    message_id: int | None
    added_at: str
    active: bool


class Database:
    def __init__(self, path: str):
        self.path = path

    def init(self) -> None:
        directory = os.path.dirname(self.path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with self._connect() as conn:
            conn.execute(_SCHEMA)

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.path)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def add_entry(self, url: str, title: str, message_id: int | None) -> bool:
        """Insert a new entry; returns False if the URL already exists (dedup)."""
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO entries (url, title, message_id, added_at) "
                "VALUES (?, ?, ?, ?) ON CONFLICT(url) DO NOTHING",
                (url, title, message_id, datetime.now(timezone.utc).isoformat()),
            )
            return cur.rowcount > 0

    def list_active(self) -> list[Entry]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, url, title, message_id, added_at, active "
                "FROM entries WHERE active = 1 ORDER BY id"
            ).fetchall()
        return [Entry(*row[:5], active=bool(row[5])) for row in rows]

    def count(self) -> int:
        with self._connect() as conn:
            (n,) = conn.execute("SELECT COUNT(*) FROM entries WHERE active = 1").fetchone()
        return n

    def deactivate(self, entry_id: int) -> None:
        # ponytail: no caller yet — this is the seam for a future admin/auth endpoint
        with self._connect() as conn:
            conn.execute("UPDATE entries SET active = 0 WHERE id = ?", (entry_id,))
