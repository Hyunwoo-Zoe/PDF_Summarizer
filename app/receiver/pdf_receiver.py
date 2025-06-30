import os, tempfile, requests
from typing import Final
from unstructured.partition.pdf import partition_pdf

_TIMEOUT: Final[int] = 30

class PDFReceiver:
    """PDF 링크 → 텍스트(이미지 OCR 포함)"""
    def fetch_and_extract_text(self, url: str) -> str:
        resp = requests.get(url, timeout=_TIMEOUT)
        resp.raise_for_status()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as fp:
            fp.write(resp.content)
            pdf_path = fp.name
        try:
            elements = partition_pdf(
                filename=pdf_path,
                strategy="hi_res",
                ocr_languages="eng+kor",
                infer_table_structure=True,
                detect_rotation_and_deskew=True,
            )
            return "\n".join(e.text for e in elements if e.text)
        finally:
            os.remove(pdf_path)

