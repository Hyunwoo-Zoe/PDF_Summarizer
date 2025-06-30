from langchain.chains.summarize import load_summarize_chain
from langchain_openai import ChatOpenAI
from app.vectordb.vector_db import VectorDB
from app.cache.cache_db import CacheDB

class SummaryService:
    def __init__(self, vector: VectorDB, cache: CacheDB):
        self.vector, self.cache = vector, cache
        self.llm = ChatOpenAI(temperature=0.3)

    def generate(self, file_id: str) -> str:
        if (c := self.cache.get_pdf(file_id)):
            return c
        docs = self.vector.get_docs(file_id)
        if not docs:
            return f"No documents found for file_id='{file_id}'."
        chain = load_summarize_chain(self.llm, chain_type="map_reduce")
        s = chain.run(docs)
        self.cache.set_pdf(file_id, s)
        return s

