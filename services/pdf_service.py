import fitz, os
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

from repositories.pdf_repository import PDFRepository
from modules.vector_store_module import VectorStoreModule
from modules.redis_cache_module import CacheModule


class PDFService:
    """
    URL 기반 요약(summarize_pdf) + 로컬 파일 기반 요약(summarize_pdf_local)
    """

    def __init__(self, cache_module: CacheModule, vector_store: VectorStoreModule):
        self.cache = cache_module
        self.vs = vector_store
        self.repo = PDFRepository(cache_module, vector_store)

        self.llm = ChatOpenAI(
            model_name="gpt-3.5-turbo", temperature=0.3, max_tokens=1000
        )
        self.prompt = PromptTemplate(
            template="다음 문서 내용:\n{text}\n\n질문:{query}\n답변:",
            input_variables=["text", "query"],
        )

    # ───────────────── 로컬 파일 요약 ─────────────────
    async def summarize_pdf_local(self, file_path: str, query: str) -> Dict[str, Any]:
        # 1) Redis 캐시 확인
        if (hit := self.cache.get(file_path, query)) is not None:
            return {"success": True, "summary": hit, "source": "cache"}

        # 2) 텍스트 추출
        try:
            with fitz.open(file_path) as doc:
                text = "\n".join(p.get_text("text") for p in doc)
        except Exception as e:
            return {"success": False, "error": f"텍스트 추출 실패: {e}"}

        # 3) LLM 요약 (큰 문서는 앞 6k token만 사용)
        try:
            prompt = self.prompt.format(text=text[:6000], query=query)
            resp = await self.llm.ainvoke(prompt)
            summary = resp.content.strip()
        except Exception as e:
            return {"success": False, "error": f"LLM 오류: {e}"}

        else:
            self.cache.set(file_path, query, summary)
            return {"success": True, "summary": summary, "source": "generated"}
        finally:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"[경고] 파일 삭제 실패: {file_path} - {e}")
    