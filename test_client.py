#!/usr/bin/env python3
"""
PDF Summary Service 클라이언트 테스트 스크립트
"""

import requests
import json
import time
from typing import Dict, Any

class PDFSummaryClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self) -> Dict[str, Any]:
        """서비스 상태 확인"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def summarize_pdf(self, pdf_url: str, query: str) -> Dict[str, Any]:
        """PDF 요약 요청"""
        try:
            payload = {
                "pdf_url": pdf_url,
                "query": query
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/summarize",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_cache_status(self) -> Dict[str, Any]:
        """캐시 상태 조회"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/cache/status")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_document_status(self, pdf_url: str) -> Dict[str, Any]:
        """문서 상태 조회"""
        try:
            payload = {"pdf_url": pdf_url}
            response = self.session.post(
                f"{self.base_url}/api/v1/document/status",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def clear_document_cache(self, pdf_url: str) -> Dict[str, Any]:
        """문서 캐시 삭제"""
        try:
            payload = {"pdf_url": pdf_url}
            response = self.session.delete(
                f"{self.base_url}/api/v1/document/cache",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

def test_pdf_summary_service():
    """PDF 요약 서비스 테스트"""
    client = PDFSummaryClient()
    
    # 테스트용 PDF URL (실제 접근 가능한 PDF URL로 변경하세요)
    test_pdf_url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
    test_query = "이 문서의 주요 내용을 요약해주세요"
    
    print("=== PDF Summary Service 테스트 시작 ===\n")
    
    # 1. 헬스 체크
    print("1. 서비스 상태 확인...")
    health = client.health_check()
    print(f"Health Check: {json.dumps(health, indent=2, ensure_ascii=False)}\n")
    
    if "error" in health:
        print("❌ 서비스에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
        return
    
    # 2. 캐시 상태 확인
    print("2. 초기 캐시 상태 확인...")
    cache_status = client.get_cache_status()
    print(f"Cache Status: {json.dumps(cache_status, indent=2, ensure_ascii=False)}\n")
    
    # 3. 문서 상태 확인
    print("3. 문서 상태 확인...")
    doc_status = client.get_document_status(test_pdf_url)
    print(f"Document Status: {json.dumps(doc_status, indent=2, ensure_ascii=False)}\n")
    
    # 4. 첫 번째 요약 요청 (캐시 미스)
    print("4. 첫 번째 요약 요청 (캐시 미스 예상)...")
    start_time = time.time()
    
    result1 = client.summarize_pdf(test_pdf_url, test_query)
    
    end_time = time.time()
    duration1 = end_time - start_time
    
    print(f"첫 번째 요약 결과 (소요시간: {duration1:.2f}초):")
    print(json.dumps(result1, indent=2, ensure_ascii=False))
    print()
    
    if result1.get("success"):
        print(f"✅ 첫 번째 요약 성공 (소스: {result1.get('source')})")
    else:
        print(f"❌ 첫 번째 요약 실패: {result1.get('error')}")
        return
    
    # 5. 두 번째 요약 요청 (캐시 히트 예상)
    print("\n5. 두 번째 요약 요청 (캐시 히트 예상)...")
    start_time = time.time()
    
    result2 = client.summarize_pdf(test_pdf_url, test_query)
    
    end_time = time.time()
    duration2 = end_time - start_time
    
    print(f"두 번째 요약 결과 (소요시간: {duration2:.2f}초):")
    print(json.dumps(result2, indent=2, ensure_ascii=False))
    print()
    
    if result2.get("success"):
        print(f"✅ 두 번째 요약 성공 (소스: {result2.get('source')})")
        
        # 캐시 효과 확인
        if result2.get('source') == 'cache':
            print(f"🚀 캐시 히트! 속도 향상: {duration1:.2f}초 → {duration2:.2f}초")
        else:
            print("⚠️  캐시 미스 - 캐시 설정을 확인하세요")
    else:
        print(f"❌ 두 번째 요약 실패: {result2.get('error')}")
    
    # 6. 다른 쿼리로 테스트
    print("\n6. 다른 쿼리로 테스트...")
    different_query = "이 문서에서 가장 중요한 포인트는 무엇인가요?"
    
    result3 = client.summarize_pdf(test_pdf_url, different_query)
    
    if result3.get("success"):
        print(f"✅ 다른 쿼리 요약 성공 (소스: {result3.get('source')})")
    else:
        print(f"❌ 다른 쿼리 요약 실패: {result3.get('error')}")
    
    # 7. 최종 캐시 상태 확인
    print("\n7. 최종 캐시 상태 확인...")
    final_cache_status = client.get_cache_status()
    print(f"Final Cache Status: {json.dumps(final_cache_status, indent=2, ensure_ascii=False)}")
    
    print("\n=== 테스트 완료 ===")

def performance_test():
    """성능 테스트 - 동일한 요청을 여러 번 보내서 캐시 효과 측정"""
    client = PDFSummaryClient()
    
    test_pdf_url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
    test_query = "문서 요약"
    
    print("=== 성능 테스트 시작 ===\n")
    
    times = []
    sources = []
    
    for i in range(5):
        print(f"요청 {i+1}/5...")
        start_time = time.time()
        
        result = client.summarize_pdf(test_pdf_url, test_query)
        
        end_time = time.time()
        duration = end_time - start_time
        
        times.append(duration)
        sources.append(result.get('source', 'unknown'))
        
        print(f"  소요시간: {duration:.2f}초, 소스: {result.get('source')}")
        
        if not result.get('success'):
            print(f"  ❌ 실패: {result.get('error')}")
            break
    
    print(f"\n=== 성능 테스트 결과 ===")
    print(f"평균 응답시간: {sum(times)/len(times):.2f}초")
    print(f"첫 번째 요청: {times[0]:.2f}초 ({sources[0]})")
    print(f"캐시 요청들: {[f'{t:.2f}초' for t in times[1:]]}")
    print(f"캐시 히트율: {sources.count('cache')}/{len(sources)} ({sources.count('cache')/len(sources)*100:.1f}%)")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "performance":
        performance_test()
    else:
        test_pdf_summary_service()