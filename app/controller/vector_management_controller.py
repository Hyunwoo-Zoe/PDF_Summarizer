from fastapi import APIRouter
from app.vectordb.vector_db import get_vector_db

router = APIRouter(prefix="/vector", tags=["vector-management"])

@router.get("/list")
async def list_documents(vdb = get_vector_db()):
    """ChromaDB에 저장된 file_id 리스트 조회"""
    return {"file_ids": vdb.list_stored_documents()}

@router.get("/statistics")
async def vector_statistics(vdb = get_vector_db()):
    """전체 vector 컬렉션 수, 목록"""
    file_ids = vdb.list_stored_documents()
    return {
        "total_collections": len(file_ids),
        "file_ids": file_ids
    }

@router.get("/check/{file_id}")
async def check_vector_exists(file_id: str, vdb = get_vector_db()):
    """특정 file_id의 벡터 컬렉션 존재 여부 확인"""
    return {
        "file_id": file_id,
        "exists": file_id in vdb.list_stored_documents()
    }

@router.delete("/delete/{file_id}")
async def delete_vector(file_id: str, vdb = get_vector_db()):
    """특정 file_id의 벡터 컬렉션 삭제"""
    success = vdb.delete_document(file_id)
    return {
        "file_id": file_id,
        "deleted": success
    }