# memory/persistent.py
import sqlite3
import json
from pathlib import Path

DB_PATH = Path("memory_store.db")


class PersistentMemory:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(DB_PATH)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._ensure_tables()

    def _ensure_tables(self):
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                conv_id TEXT PRIMARY KEY,
                history TEXT,
                updated_ts TEXT
            )
            """
        )
        self.conn.commit()

    def save_feature(self, feature_id: str, data: dict):
        cur = self.conn.cursor()
        cur.execute(
            "REPLACE INTO features (feature_id, data, updated_ts) VALUES (?, ?, datetime('now'))",
            (feature_id, json.dumps(data)),
        )
        self.conn.commit()

    def get_feature(self, feature_id: str):
        cur = self.conn.cursor()
        cur.execute("SELECT data FROM features WHERE feature_id = ?", (feature_id,))
        row = cur.fetchone()
        return json.loads(row[0]) if row else None

    def list_features(self):
        cur = self.conn.cursor()
        cur.execute("SELECT feature_id, updated_ts FROM features ORDER BY updated_ts DESC")
        return cur.fetchall()

    def save_conversation(self, conv_id: str, history: list):
        cur = self.conn.cursor()
        cur.execute(
            "REPLACE INTO conversations (conv_id, history, updated_ts) VALUES (?, ?, datetime('now'))",
            (conv_id, json.dumps(history)),
        )
        self.conn.commit()

    def load_conversation(self, conv_id: str):
        cur = self.conn.cursor()
        cur.execute("SELECT history FROM conversations WHERE conv_id = ?", (conv_id,))
        row = cur.fetchone()
        return json.loads(row[0]) if row else None