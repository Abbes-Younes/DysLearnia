import fitz  # PyMuPDF
from typing import List


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract all text from a PDF given its raw bytes.
    Returns a single string with page breaks marked.
    """
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    pages = []
    for page in doc:
        text = page.get_text("text").strip()
        if text:
            pages.append(text)
    doc.close()
    return "\n\n---\n\n".join(pages)


def chunk_text(text: str, max_chars: int = 1500) -> List[str]:
    """
    Split text into chunks of max_chars characters.
    Tries to split on paragraph boundaries first.
    This keeps context coherent for the LLM.
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
            # If a single paragraph is too long, hard-split it
            if len(para) > max_chars:
                for i in range(0, len(para), max_chars):
                    chunks.append(para[i:i + max_chars])
            else:
                current = para

    if current:
        chunks.append(current)

    return chunks
