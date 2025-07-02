
import hashlib
from typing import Optional, Dict, Any
import redis
import os

class CacheModule:
    def __init__(
        self,
        host: str = os.getenv("REDIS_HOST", "redis"),
        port: int = 6379,
        db: int = 0,
        ttl_sec: int = 60 * 60 * 24 * 7,  # 7일
    ):
        self.r = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.ttl = ttl_sec

    # ───────────────── 키 생성 ──────────────────
    @staticmethod
    def _key(pdf: str, query: str) -> str:
        return hashlib.sha256(f"{pdf}_{query}".encode()).hexdigest()

    # ───────────────── CRUD ─────────────────────
    def get(self, pdf: str, query: str) -> Optional[str]:
        return self.r.get(self._key(pdf, query))

    def set(self, pdf: str, query: str, summary: str) -> None:
        k = self._key(pdf, query)
        self.r.set(k, summary, ex=self.ttl)

    # PDFRepository 가 기대하는 부가 메서드
    def exists(self, pdf: str, query: str) -> bool:
        return self.r.exists(self._key(pdf, query)) == 1

    def clear(self):
        self.r.flushdb()

    def get_stats(self) -> Dict[str, Any]:
        return self.r.info()
