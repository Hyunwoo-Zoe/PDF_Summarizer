from fastapi import APIRouter, Depends
from app.model.chat_summary_dto import ChatSummaryRequestDTO
from app.cache.cache_db import get_cache_db
from app.service.chat_summary_service import ChatSummaryService

router = APIRouter()

@router.post("/chat-summary")
async def summarize_chat(
    req: ChatSummaryRequestDTO,
    cache = Depends(get_cache_db),
):
    summary = ChatSummaryService(cache).generate(req.chat_id, req.messages)
    return {"chat_id": req.chat_id, "summary": summary}

