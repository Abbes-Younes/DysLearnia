import pytesseract
from PIL import Image
import os
from pdf2image import convert_from_path


class OCRAgent:

    def __init__(self, lang="eng+fra"):
        self.lang = lang

    def extract_text(self, file_path):

        ext = os.path.splitext(file_path)[1].lower()

        if ext in [".png", ".jpg", ".jpeg"]:
            img = Image.open(file_path).convert("L")
            text = pytesseract.image_to_string(img, lang=self.lang)

        elif ext == ".pdf":
            text = self._pdf_to_text(file_path)

        else:
            return ""

        return " ".join(text.split())

    def _pdf_to_text(self, file_path):
        """Extract text from PDF via OCR. Uses pdf2image; fallback to PyMuPDF if poppler missing."""
        try:
            pages = convert_from_path(file_path)
        except Exception:
            # Fallback when poppler is not installed (e.g. Windows)
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(file_path)
                text = ""
                for page in doc:
                    pix = page.get_pixmap(dpi=150)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    img = img.convert("L")
                    text += pytesseract.image_to_string(img, lang=self.lang) + " "
                doc.close()
                return " ".join(text.split())
            except ImportError:
                raise RuntimeError(
                    "PDF needs poppler (add to PATH) or install PyMuPDF: pip install PyMuPDF"
                )
        text = ""
        for page in pages:
            page = page.convert("L")
            text += pytesseract.image_to_string(page, lang=self.lang)
        return " ".join(text.split())