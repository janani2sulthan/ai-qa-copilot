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

        # Feature table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS features (
                feature_id TEXT PRIMARY KEY,
                data TEXT,
                updated_ts TEXT
            )
        """)

        # Conversation table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                conv_id TEXT PRIMARY KEY,
                history TEXT,          -- JSON list of {role, text}
                updated_ts TEXT
            )
        """)

        self.conn.commit()

    # ---------------------------------------------------------
    # FEATURE MEMORY
    # ---------------------------------------------------------
    def save_feature(self, feature_id: str, data: dict):
        cur = self.conn.cursor()
        cur.execute(
            "REPLACE INTO features (feature_id, data, updated_ts) "
            "VALUES (?, ?, datetime('now'))",
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

    # ---------------------------------------------------------
    # CONVERSATION MEMORY
    # ---------------------------------------------------------
    def save_conversation(self, conv_id: str, history: list):
        """Store entire conversation history as JSON."""
        cur = self.conn.cursor()
        cur.execute(
            "REPLACE INTO conversations (conv_id, history, updated_ts) "
            "VALUES (?, ?, datetime('now'))",
            (conv_id, json.dumps(history)),
        )
        self.conn.commit()

    def load_conversation(self, conv_id: str):
        """Return list of past messages, or empty list."""
        cur = self.conn.cursor()
        cur.execute("SELECT history FROM conversations WHERE conv_id = ?", (conv_id,))
        row = cur.fetchone()
        if not row:
            return []
        try:
            return json.loads(row[0])
        except Exception:
            return []