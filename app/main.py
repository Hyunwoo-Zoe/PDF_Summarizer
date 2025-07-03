
from fastapi import FastAPI
from app.controller import pdf_summary_controller, chat_summary_controller, cache_management_controller, vector_management_controller

app = FastAPI(title="Multi-Summary API")
app.include_router(pdf_summary_controller.router)
app.include_router(chat_summary_controller.router)
app.include_router(cache_management_controller.router)
app.include_router(vector_management_controller.router)
