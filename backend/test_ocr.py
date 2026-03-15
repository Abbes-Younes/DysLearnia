import pytesseract
from PIL import Image, ImageDraw

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

print("Step 1: Creating test image...")
img = Image.new("RGB", (400, 100), color="white")
draw = ImageDraw.Draw(img)
draw.text((10, 40), "Hello test", fill="black")
print("Step 2: Running OCR...")

try:
    result = pytesseract.image_to_string(img)
    print(f"SUCCESS: '{result.strip()}'")
except Exception as e:
    print(f"FAILED: {e}")
