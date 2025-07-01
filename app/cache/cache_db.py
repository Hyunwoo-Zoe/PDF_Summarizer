import redis
from functools import lru_cache
from typing import Optional

class RedisCacheDB:
    def __init__(self, host="localhost", port=6379, db=0):
        self.r = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    def get_pdf(self, fid: str) -> Optional[str]:
        return self.r.get(f"pdf:{fid}")

    def set_pdf(self, fid: str, s: str):
        self.r.set(f"pdf:{fid}", s)

    def get_chat(self, cid: str) -> Optional[str]:
        return None  # 비활성화

    def set_chat(self, cid: str, s: str):
        pass  # 비활성화

@lru_cache(maxsize=1)
def get_cache_db() -> "RedisCacheDB":
    return RedisCacheDB()

