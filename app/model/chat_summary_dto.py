from typing import List
from pydantic import BaseModel

class ChatSummaryRequestDTO(BaseModel):
    chat_id: str
    messages: List[str]

