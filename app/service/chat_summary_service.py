from langchain.chains.summarize import load_summarize_chain
from langchain_openai import ChatOpenAI
from langchain.schema import Document

class ChatSummaryService:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0.3)

    def generate(self, messages: list[str]) -> str:
        combined_text = "\n".join(messages)
        docs = [Document(page_content=combined_text)]
        chain = load_summarize_chain(self.llm, chain_type="stuff")
        summary = chain.run(docs)
        return summary

