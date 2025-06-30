import sqlite3
from functools import lru_cache
from typing import Optional

_SCHEMA = """
CREATE TABLE IF NOT EXISTS pdf_summaries (
    file_id TEXT PRIMARY KEY,
    summary TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS chat_summaries (
    chat_id TEXT PRIMARY KEY,
    summary TEXT NOT NULL
);
"""

class CacheDB:
    def __init__(self, path="./summary_cache.db"):
        self.conn = sqlite3.connect(path, check_same_thread=False, isolation_level=None)
        self.conn.executescript(_SCHEMA)

    # PDF
    def get_pdf(self, fid: str) -> Optional[str]:
        r = self.conn.execute(
            "SELECT summary FROM pdf_summaries WHERE file_id=?", (fid,)
        ).fetchone()
        return r[0] if r else None
    def set_pdf(self, fid: str, s: str):
        self.conn.execute(
            "INSERT OR REPLACE INTO pdf_summaries VALUES (?,?)", (fid, s)
        )

    # Chat
    def get_chat(self, cid: str) -> Optional[str]:
        r = self.conn.execute(
            "SELECT summary FROM chat_summaries WHERE chat_id=?", (cid,)
        ).fetchone()
        return r[0] if r else None
    def set_chat(self, cid: str, s: str):
        self.conn.execute(
            "INSERT OR REPLACE INTO chat_summaries VALUES (?,?)", (cid, s)
        )

@lru_cache(maxsize=1)
def get_cache_db() -> "CacheDB":
    return CacheDB()

