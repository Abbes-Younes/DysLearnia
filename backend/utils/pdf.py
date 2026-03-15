import os
import fitz  # PyMuPDF
from typing import List
from PIL import Image
import pytesseract
import io

# Set tesseract path (Windows)
tesseract_path = os.getenv("TESSERACT_PATH", "tesseract")
pytesseract.pytesseract.tesseract_cmd = tesseract_path

print(f"[pdf] Using tesseract at: {tesseract_path}")


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text from any PDF using PyMuPDF + Tesseract only.
    PyMuPDF renders each page to an image at 300 DPI.
    Tesseract reads the image and extracts text.
    No Poppler or pdf2image needed.
    """
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    print(f"[pdf] Opened PDF — {doc.page_count} pages")

    pages = []
    for i, page in enumerate(doc):
        print(f"[pdf] OCR page {i + 1}/{doc.page_count}...")

        # Render page to image at 300 DPI using PyMuPDF
        mat = fitz.Matrix(300 / 72, 300 / 72)  # 300 DPI scale
        pix = page.get_pixmap(matrix=mat)

        # Convert PyMuPDF pixmap to PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Run Tesseract OCR on the image
        text = pytesseract.image_to_string(img, lang="eng").strip()

        if text:
            pages.append(text)

    doc.close()

    if not pages:
        raise ValueError(
            "OCR found no text in this PDF. "
            "Make sure Tesseract is installed correctly."
        )

    print(f"[pdf] OCR complete — {len(pages)} pages with text")
    return "\n\n---\n\n".join(pages)


def chunk_text(text: str, max_chars: int = 1500) -> List[str]:
    """
    Split text into chunks of max_chars.
    Splits on paragraph boundaries where possible.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 2 <= max_chars:
            current += ("\n\n" if current else "") + para
        else:
            if current:
                chunks.append(current)
            if len(para) > max_chars:
                for i in range(0, len(para), max_chars):
                    chunks.append(para[i:i + max_chars])
            else:
                current = para

    if current:
        chunks.append(current)

    return chunks