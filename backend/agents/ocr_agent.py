# backend/agents/ocr_agent.py

import pytesseract
from PIL import Image
import os
from pdf2image import convert_from_path  # for PDF support

class OCRAgent:
    def __init__(self, lang='eng+fra'):
        """
        OCR Agent to extract text from images or PDFs.
        lang: Language code for Tesseract (default 'eng')
        """
        self.lang = lang

    def extract_text_from_image(self, image_path):
        """
        Extract text from a single image.
        Returns cleaned text string.
        """
        try:
            img = Image.open(image_path)
            img = img.convert('L')  # grayscale for better OCR accuracy
            raw_text = pytesseract.image_to_string(img, lang=self.lang)
            # Clean text: remove extra spaces/newlines
            cleaned_text = " ".join(raw_text.split())
            return cleaned_text
        except Exception as e:
            print(f"[OCRAgent] Error reading image: {e}")
            return ""

    def extract_text_from_pdf(self, pdf_path, dpi=300):
        """
        Extract text from each page of a PDF.
        Returns concatenated cleaned text from all pages.
        """
        try:
            pages = convert_from_path(pdf_path, dpi=dpi)
            all_text = ""
            for page in pages:
                page = page.convert('L')
                text = pytesseract.image_to_string(page, lang=self.lang)
                all_text += " " + " ".join(text.split())
            return all_text
        except Exception as e:
            print(f"[OCRAgent] Error reading PDF: {e}")
            return ""

    def extract_text(self, input_path):
        """
        Detect file type (image or PDF) and extract text.
        """
        ext = os.path.splitext(input_path)[1].lower()
        if ext in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
            return self.extract_text_from_image(input_path)
        elif ext == '.pdf':
            return self.extract_text_from_pdf(input_path)
        else:
            print(f"[OCRAgent] Unsupported file type: {ext}")
            return ""