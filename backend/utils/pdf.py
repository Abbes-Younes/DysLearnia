import os
import fitz  # PyMuPDF
from typing import List
from pdf2image import convert_from_bytes
import pytesseract
from PIL import Image

# Set tesseract path (required on Windows)
tesseract_path = os.getenv("TESSERACT_PATH", "tesseract")
pytesseract.pytesseract.tesseract_cmd = tesseract_path


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Always runs OCR on every page.
    Converts each PDF page to an image at 300 DPI,
    then runs pytesseract on each image.
    Works on both normal PDFs and scanned PDFs.
    """
    print("[pdf] Converting PDF pages to images...")
    images = convert_from_bytes(file_bytes, dpi=300)
    print(f"[pdf] Got {len(images)} pages — running OCR...")

    pages = []
    for i, image in enumerate(images):
        print(f"[pdf] OCR page {i + 1}/{len(images)}...")
        text = pytesseract.image_to_string(image, lang="eng").strip()
        if text:
            pages.append(text)

    if not pages:
        raise ValueError(
            "OCR found no text in this PDF. "
            "Check that the PDF is not blank or corrupted."
        )

    print(f"[pdf] OCR complete — {len(pages)} pages extracted")
    return "\n\n---\n\n".join(pages)


def chunk_text(text: str, max_chars: int = 1500) -> List[str]:
    """
    Split text into chunks of max_chars.
    Splits on paragraph boundaries where possible
    so each chunk is a coherent block of content.
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
            # Paragraph itself is too long — hard split
            if len(para) > max_chars:
                for i in range(0, len(para), max_chars):
                    chunks.append(para[i:i + max_chars])
            else:
                current = para

    if current:
        chunks.append(current)

    return chunks