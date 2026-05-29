import pypdf
from docx import Document as DocxDocument


def extract_text(file_path: str, mime_type: str) -> str:
    if mime_type == "application/pdf" or file_path.endswith(".pdf"):
        return _extract_pdf(file_path)
    if mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document" or file_path.endswith(".docx"):
        return _extract_docx(file_path)
    return _extract_txt(file_path)


def _extract_pdf(file_path: str) -> str:
    reader = pypdf.PdfReader(file_path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _extract_docx(file_path: str) -> str:
    doc = DocxDocument(file_path)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def _extract_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()
