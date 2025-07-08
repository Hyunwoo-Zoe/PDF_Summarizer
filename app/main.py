
# app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.background.cleanup_scheduler import register_cleanup_task
from app.controller import (
    pdf_summary_controller,
    chat_summary_controller,
    cache_management_controller,
    vector_management_controller,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = register_cleanup_task()
    try:
        yield
    finally:
        task.cancel()

app = FastAPI(title="Multi-Summary API", lifespan=lifespan)

app.include_router(pdf_summary_controller.router)
app.include_router(chat_summary_controller.router)
app.include_router(cache_management_controller.router)
app.include_router(vector_management_controller.router)

