from typing import Optional, List, Dict, Any
from langchain.schema import Document

from modules.redis_cache_module import CacheModule
from modules.vector_store_module import VectorStoreModule

class PDFRepository:
    """
    PDF 관련 데이터 접근을 담당하는 Repository 클래스
    캐시 모듈과 벡터스토어 모듈과의 상호작용을 관리
    """

    def __init__(self, cache_module: CacheModule, vector_store_module: VectorStoreModule):
        self.cache_module = cache_module
        self.vector_store_module = vector_store_module

    def get_cached_summary(self, pdf_url: str, query: str) -> Optional[str]:
        return self.cache_module.get(pdf_url, query)

    def cache_summary(self, pdf_url: str, query: str, summary: str) -> None:
        self.cache_module.set(pdf_url, query, summary)

    def is_summary_cached(self, pdf_url: str, query: str) -> bool:
        return self.cache_module.exists(pdf_url, query)

    def store_document_if_not_exists(self, pdf_url: str, text_content: str) -> bool:
        doc_info = self.vector_store_module.get_document_info(pdf_url)
        if doc_info.get("stored", False):
            return True
        return self.vector_store_module.store_document(pdf_url, text_content)

    def search_relevant_chunks(self, pdf_url: str, query: str, k: int = 5) -> List[Document]:
        return self.vector_store_module.search_similar_chunks(pdf_url, query, k)

    def get_document_info(self, pdf_url: str) -> Dict[str, Any]:
        return self.vector_store_module.get_document_info(pdf_url)

    def delete_document_vectors(self, pdf_url: str) -> bool:
        return self.vector_store_module.delete_document(pdf_url)

    def get_cache_stats(self) -> Dict[str, Any]:
        return self.cache_module.get_stats()

    def clear_cache(self) -> None:
        self.cache_module.clear()

    def get_all_stored_documents(self) -> List[str]:
        return self.vector_store_module.list_stored_documents()

    def is_document_vectorized(self, pdf_url: str) -> bool:
        doc_info = self.get_document_info(pdf_url)
        return doc_info.get("stored", False)

    def get_document_chunk_count(self, pdf_url: str) -> int:
        doc_info = self.get_document_info(pdf_url)
        return doc_info.get("chunk_count", 0)
