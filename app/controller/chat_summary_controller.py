from fastapi import APIRouter
from app.model.chat_summary_dto import ChatSummaryRequestDTO
from app.service.chat_summary_service import ChatSummaryService

router = APIRouter()

@router.post("/chat-summary")
async def summarize_chat(req: ChatSummaryRequestDTO):
    sorted_chats = sorted(req.chats, key=lambda chat: chat.timestamp)
    messages = [
        f"[{chat.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {chat.sender}: {chat.plaintext}"
        for chat in sorted_chats
    ]
    summary = ChatSummaryService().generate(messages)
    return {"summary": summary}

