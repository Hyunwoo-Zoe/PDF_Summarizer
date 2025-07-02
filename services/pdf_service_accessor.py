from typing import Optional
from services.pdf_service import PDFService

_pdf_service: Optional[PDFService] = None


def set_pdf_service(service: PDFService):
    global _pdf_service
    _pdf_service = service


def get_pdf_service() -> PDFService:
    if _pdf_service is None:
        raise RuntimeError("PDFService not initialized")
    return _pdf_service
