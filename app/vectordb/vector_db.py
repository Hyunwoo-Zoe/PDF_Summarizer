# app/vectordb/vector_db.py
from functools import lru_cache
from typing import List

# ① Embedding: 새 패키지가 설치돼 있으면 우선 사용
try:
    from langchain_huggingface import HuggingFaceEmbeddings        # 선택 사항
except ModuleNotFoundError:
    from langchain_community.embeddings import HuggingFaceEmbeddings  # 기본

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_chroma import Chroma

# ───────── 설정 상수 ───────────────────────────────
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
PERSIST_DIR = "./chroma_db"      # 디스크에 영구 저장되는 경로

# ───────── Chroma 래퍼 ────────────────────────────
class VectorDB:
    """
    * langchain-chroma 0.0.x  ~ 0.1.x  ~ 0.4.x  모두 호환
    * persist() API 변화 자동 감지
    """

    def __init__(self) -> None:
        self.embed = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # LangChain 래퍼: persist_directory 지정 → 디스크 기반
        self.db: Chroma = Chroma(
            persist_directory=PERSIST_DIR,
            embedding_function=self.embed,
        )

        # persist 위치(버전별)를 한 번만 탐색해 함수 포인터로 저장
        if hasattr(self.db, "persist"):  # 0.0.x
            self._persist = self.db.persist
        elif getattr(self.db, "client", None) and hasattr(self.db.client, "persist"):
            self._persist = self.db.client.persist  # 0.1.x
        else:                                      # 0.4.x 이상 (자동 flush)
            self._persist = lambda: None

    # ───────────────────────────────────────────────
    def store(self, text: str, file_id: str) -> None:
        """텍스트를 청크 → 임베딩 → Chroma 저장(덮어쓰기)."""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
        )

        # 1) 동일 file_id 문서가 있으면 삭제
        self.db.delete(where={"file_id": file_id})

        # 2) 텍스트를 Document 배열로 변환 후 저장
        docs = [
            Document(page_content=chunk, metadata={"file_id": file_id})
            for chunk in splitter.split_text(text)
        ]
        self.db.add_documents(docs)

        # 3) 버전에 맞게 영구화(없으면 no-op)
        self._persist()

    # ───────────────────────────────────────────────
    def get_docs(self, file_id: str) -> List[Document]:
        """file_id로 저장된 모든 청크를 LangChain Document 배열로 반환."""
        raw = self.db.get(include=["documents"], where={"file_id": file_id})
        docs = raw.get("documents", [])

        # langchain-chroma 0.1.x REST 모드 → 문자열 리스트, 임베디드 모드 → Document 객체
        if docs and isinstance(docs[0], Document):
            return docs
        return [Document(page_content=t) for t in docs]


# ───────── FastAPI DI 싱글톤 ───────────────────────
@lru_cache(maxsize=1)
def get_vector_db() -> "VectorDB":
    return VectorDB()

