from langchain.chains.summarize import load_summarize_chain
from langchain_openai import ChatOpenAI
from langchain.schema import Document
from app.cache.cache_db import CacheDB

class ChatSummaryService:
    def __init__(self, cache: CacheDB):
        self.cache = cache
        self.llm = ChatOpenAI(temperature=0.3)

    def generate(self, chat_id: str, messages: list[str]) -> str:
        if (c := self.cache.get_chat(chat_id)):
            return c
        docs = [Document(page_content="\n".join(messages))]
        chain = load_summarize_chain(self.llm, chain_type="stuff")
        s = chain.run(docs)
        self.cache.set_chat(chat_id, s)
        return s

