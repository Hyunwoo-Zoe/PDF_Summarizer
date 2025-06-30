from functools import lru_cache
from typing import List

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_chroma import Chroma

CHUNK_SIZE, CHUNK_OVERLAP, PERSIST_DIR = 500, 50, "./chroma_db"

class VectorDB:
    def __init__(self):
        self.embedding_function = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.db = Chroma(
            persist_directory=PERSIST_DIR,
            embedding_function=self.embedding_function,
        )

    def store(self, text: str, file_id: str):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
        )
        self.db.delete(where={"file_id": file_id})
        docs: List[Document] = [
            Document(page_content=c, metadata={"file_id": file_id})
            for c in splitter.split_text(text)
        ]
        self.db.add_documents(docs)
        self.db.persist()

    def get_docs(self, file_id: str) -> List[Document]:
        return self.db.get(include=["documents"], where={"file_id": file_id})["documents"]

@lru_cache(maxsize=1)
def get_vector_db() -> "VectorDB":
    return VectorDB()

