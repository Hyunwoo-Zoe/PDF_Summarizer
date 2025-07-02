from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
import os, shutil, uuid

from services.pdf_service_accessor import get_pdf_service
from services.pdf_service import PDFService

router = APIRouter(tags=["PDF Summary"])
UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_and_summarize(
    file: UploadFile = File(...),
    query: str = Form(...),
    pdf_service: PDFService = Depends(get_pdf_service),
):
    try:
        fname = f"{uuid.uuid4()}_{file.filename}"
        path = os.path.join(UPLOAD_DIR, fname)
        with open(path, "wb") as buf:
            shutil.copyfileobj(file.file, buf)

        result = await pdf_service.summarize_pdf_local(path, query)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"업로드 실패: {e}")
