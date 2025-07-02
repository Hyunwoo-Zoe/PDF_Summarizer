import os
import redis
from functools import lru_cache
from typing import Optional

class RedisCacheDB:
    def __init__(
        self,
        host: str = os.getenv("REDIS_HOST", "localhost"),
        port: int = int(os.getenv("REDIS_PORT", "6379")),
        db: int = int(os.getenv("REDIS_DB", "0")),
        ttl_sec: int = int(os.getenv("REDIS_TTL", str(60 * 60 * 24 * 7)))  # 7일 기본
    ):
        self.r = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.ttl = ttl_sec

    def get_pdf(self, fid: str) -> Optional[str]:
        return self.r.get(f"pdf:{fid}")

    def set_pdf(self, fid: str, s: str):
        self.r.set(f"pdf:{fid}", s, ex=self.ttl)  # TTL 적용

    def get_chat(self, cid: str) -> Optional[str]:
        return None  # 비활성화

    def set_chat(self, cid: str, s: str):
        pass  # 비활성화

@lru_cache(maxsize=1)
def get_cache_db() -> "RedisCacheDB":
    return RedisCacheDB()

