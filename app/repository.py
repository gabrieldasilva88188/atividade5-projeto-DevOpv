"""Persistência em SQLite — exercitada pelos testes de integração."""
import json
import sqlite3
from datetime import datetime, timezone


class SqliteTaskRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _connect(self):
        conn = sqlite3.connect(self.db_path, timeout=30)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        conn = self._connect()
        try:
            with conn:
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute(
                    """CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        priority TEXT NOT NULL,
                        tags TEXT NOT NULL,
                        done INTEGER NOT NULL DEFAULT 0,
                        created_at TEXT NOT NULL
                    )"""
                )
        finally:
            conn.close()

    @staticmethod
    def _to_dict(row):
        return {
            "id": row["id"],
            "title": row["title"],
            "priority": row["priority"],
            "tags": json.loads(row["tags"]),
            "done": bool(row["done"]),
            "created_at": row["created_at"],
        }

    def add(self, title, priority, tags):
        now = datetime.now(timezone.utc).isoformat()
        conn = self._connect()
        try:
            with conn:
                cur = conn.execute(
                    "INSERT INTO tasks (title, priority, tags, done, created_at) VALUES (?, ?, ?, 0, ?)",
                    (title, priority, json.dumps(tags), now),
                )
                task_id = cur.lastrowid
        finally:
            conn.close()
        return self.get(task_id)

    def get(self, task_id):
        conn = self._connect()
        try:
            row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        finally:
            conn.close()
        return self._to_dict(row) if row else None

    def list(self, done=None):
        query, params = "SELECT * FROM tasks", ()
        if done is not None:
            query += " WHERE done = ?"
            params = (1 if done else 0,)
        query += " ORDER BY id"
        conn = self._connect()
        try:
            rows = conn.execute(query, params).fetchall()
        finally:
            conn.close()
        return [self._to_dict(r) for r in rows]

    def mark_done(self, task_id):
        conn = self._connect()
        try:
            with conn:
                conn.execute("UPDATE tasks SET done = 1 WHERE id = ?", (task_id,))
        finally:
            conn.close()
        return self.get(task_id)

    def delete(self, task_id):
        conn = self._connect()
        try:
            with conn:
                cur = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                deleted = cur.rowcount > 0
        finally:
            conn.close()
        return deleted
