
# app/main.py

from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
from datetime import datetime, timedelta

from app.controller import (
    pdf_summary_controller,
    chat_summary_controller,
    cache_management_controller,
    vector_management_controller
)
from app.vectordb.vector_db import get_vector_db
from app.cache.cache_db import get_cache_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    async def cleanup_job():
        # ✅ (1) 서버 켜지자마자 즉시 한 번 정리
        vdb = get_vector_db()
        cache = get_cache_db()
        deleted = vdb.cleanup_unused_vectors(cache)
        if deleted:
            print(f"[Startup Cleanup] Deleted {len(deleted)} vector(s): {deleted}")
        else:
            print(f"[Startup Cleanup] No vector deleted at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # ✅ (2) 다음 새벽 3시까지 기다림
        while True:
            now = datetime.now()
            next_run = (now + timedelta(days=1)).replace(hour=3, minute=0, second=0, microsecond=0)
            if now.hour < 3:
                next_run = now.replace(hour=3, minute=0, second=0, microsecond=0)

            delay = (next_run - now).total_seconds()
            print(f"[Auto Cleanup] Waiting {delay / 3600:.2f} hours until next cleanup at 03:00")

            await asyncio.sleep(delay)

            # ✅ (3) 매일 03:00 정리 실행
            vdb = get_vector_db()
            cache = get_cache_db()
            deleted = vdb.cleanup_unused_vectors(cache)
            if deleted:
                print(f"[Auto Cleanup] Deleted {len(deleted)} vector(s): {deleted}")
            else:
                print(f"[Auto Cleanup] No vector deleted at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            await asyncio.sleep(86400)  # 다음 정리는 24시간 후

    asyncio.create_task(cleanup_job())  # ⏱ 백그라운드 작업 등록
    yield

# ✅ lifespan이 연결된 FastAPI 앱 생성
app = FastAPI(title="Multi-Summary API", lifespan=lifespan)

# ✅ 기존 라우터 등록
app.include_router(pdf_summary_controller.router)
app.include_router(chat_summary_controller.router)
app.include_router(cache_management_controller.router)
app.include_router(vector_management_controller.router)
