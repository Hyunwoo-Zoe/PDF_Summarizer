import os
import hashlib
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
import threading

class VectorStoreModule:
    """
    PDF 문서의 벡터 임베딩을 관리하는 모듈
    외부 ChromaDB HTTP API 서버를 사용하여 문서 임베딩 저장 및 유사성 검색 수행
    """

    def __init__(self):
        # ────── 설정: 외부 ChromaDB 컨테이너와 연결 ──────
        chroma_host = os.getenv("CHROMA_HOST", "localhost")
        chroma_port = int(os.getenv("CHROMA_PORT", "8000"))
        self.client = chromadb.HttpClient(
            host=chroma_host,
            port=chroma_port,
           )

        # ────── 임베딩 및 텍스트 분할기 설정 ──────
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self._lock = threading.RLock()

    def _get_collection_name(self, pdf_url: str) -> str:
        """PDF URL을 기반으로 컬렉션 이름 생성"""
        url_hash = hashlib.md5(pdf_url.encode()).hexdigest()
        return f"pdf_collection_{url_hash}"

    def _get_vectorstore(self, collection_name: str) -> Chroma:
        """특정 컬렉션에 대한 벡터스토어 반환"""
        return Chroma(
            client=self.client,
            collection_name=collection_name,
            embedding_function=self.embeddings,
        )

    def store_document(self, pdf_url: str, text_content: str) -> bool:
        """문서를 청크로 분할하여 벡터스토어에 저장"""
        try:
            with self._lock:
                collection_name = self._get_collection_name(pdf_url)

                # 이미 저장된 문서인지 확인
                if self._is_document_stored(collection_name):
                    return True

                # 텍스트를 청크로 분할
                chunks = self.text_splitter.split_text(text_content)

                # Document 객체 생성
                documents = [
                    Document(
                        page_content=chunk,
                        metadata={
                            "pdf_url": pdf_url,
                            "chunk_index": i,
                            "total_chunks": len(chunks)
                        }
                    )
                    for i, chunk in enumerate(chunks)
                ]

                # 벡터스토어에 저장
                vectorstore = self._get_vectorstore(collection_name)
                vectorstore.add_documents(documents)

                return True

        except Exception as e:
            print(f"Error storing document: {e}")
            return False

    def search_similar_chunks(self, pdf_url: str, query: str, k: int = 5) -> List[Document]:
        """쿼리와 유사한 청크들을 검색"""
        try:
            with self._lock:
                collection_name = self._get_collection_name(pdf_url)

                if not self._is_document_stored(collection_name):
                    return []

                vectorstore = self._get_vectorstore(collection_name)
                similar_docs = vectorstore.similarity_search(query=query, k=k)
                return similar_docs

        except Exception as e:
            print(f"Error searching similar chunks: {e}")
            return []

    def _is_document_stored(self, collection_name: str) -> bool:
        """문서가 이미 저장되어 있는지 확인"""
        try:
            collection = self.client.get_collection(collection_name)
            return collection.count() > 0
        except Exception:
            return False

    def delete_document(self, pdf_url: str) -> bool:
        """특정 문서의 벡터 데이터 삭제"""
        try:
            with self._lock:
                collection_name = self._get_collection_name(pdf_url)
                self.client.delete_collection(collection_name)
                return True
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False

    def get_document_info(self, pdf_url: str) -> Dict[str, Any]:
        """문서 정보 조회"""
        try:
            collection_name = self._get_collection_name(pdf_url)

            if not self._is_document_stored(collection_name):
                return {"stored": False}

            collection = self.client.get_collection(collection_name)
            count = collection.count()

            return {
                "stored": True,
                "chunk_count": count,
                "collection_name": collection_name
            }

        except Exception as e:
            print(f"Error getting document info: {e}")
            return {"stored": False, "error": str(e)}

    def list_stored_documents(self) -> List[str]:
        """저장된 모든 문서의 컬렉션 이름 목록 반환"""
        try:
            collections = self.client.list_collections()
            return [col.name for col in collections if col.name.startswith("pdf_collection_")]
        except Exception as e:
            print(f"Error listing documents: {e}")
            return []
