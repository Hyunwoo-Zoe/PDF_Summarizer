
from fastapi import FastAPI
from contextlib import asynccontextmanager
import threading, schedule, time, os
from dotenv import load_dotenv

from controllers.pdf_controller import router as pdf_router
from modules.redis_cache_module import CacheModule
from modules.vector_store_module import VectorStoreModule
from services.pdf_service import PDFService
from services.pdf_service_accessor import set_pdf_service

load_dotenv()

cache_module = None
vector_store_module = None

def reset_cache():
    if cache_module:
        cache_module.clear()
        print("Cache cleared at midnight")

def schedule_cache_reset():
    schedule.every().day.at("00:00").do(reset_cache)
    while True:
        schedule.run_pending()
        time.sleep(60)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global cache_module, vector_store_module

    cache_module = CacheModule(host=os.getenv("REDIS_HOST", "redis"))
    vector_store_module = VectorStoreModule()
    service = PDFService(cache_module, vector_store_module)
    set_pdf_service(service)

    threading.Thread(target=schedule_cache_reset, daemon=True).start()
    print("PDF Summary Service started")
    yield
    print("PDF Summary Service stopped")

app = FastAPI(
    title="PDF Summary Service",
    description="PDF 문서 요약 서비스 API",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(pdf_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "healthy"}
