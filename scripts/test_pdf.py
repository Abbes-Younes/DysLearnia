#!/usr/bin/env python3
"""
Test the full pipeline (OCR -> simplify -> audio) on the sample PDF in data folder.

Uses: backend/data/sample_texts/Resume_Communication.pdf

Requirements:
  - Tesseract installed and in PATH (OCR)
  - Ollama running with e.g. qwen3.5 (simplify, quiz)
  - Coqui TTS / pip install TTS (audio)

Run from project root:
  set PYTHONPATH=backend  && python scripts/test_pdf.py
  (Linux/Mac: PYTHONPATH=backend python scripts/test_pdf.py)
"""
import sys
from pathlib import Path

# Ensure backend is on path so agents/models resolve
_project_root = Path(__file__).resolve().parent.parent
_backend = _project_root / "backend"
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

# Sample PDF in data folder
PDF_PATH = _backend / "data" / "sample_texts" / "Resume_Communication.pdf"


def main():
    if not PDF_PATH.exists():
        print(f"PDF not found: {PDF_PATH}")
        sys.exit(1)

    print("Using PDF:", PDF_PATH)
    print("Running pipeline: OCR -> simplify -> audio...\n")

    from agents.orchestrator import pipeline

    result = pipeline.process_course(file_path=str(PDF_PATH))

    if result.get("error"):
        err = result["error"]
        print("Error:", err)
        if "poppler" in err.lower() or "page count" in err.lower():
            print("\nPDF: Install Poppler or PyMuPDF (pip install PyMuPDF).")
        if "tesseract" in err.lower():
            print("\nOCR: Install Tesseract and add it to PATH:")
            print("  https://github.com/UB-Mannheim/tesseract/wiki")
        sys.exit(1)

    raw = result.get("raw_text") or ""
    simplified = result.get("simplified_text") or ""
    audio_path = result.get("audio_path") or ""

    print("--- RAW TEXT (OCR) ---")
    print((raw[:1500] + "..." if len(raw) > 1500 else raw) or "(empty)")
    print()

    print("--- SIMPLIFIED TEXT ---")
    print((simplified[:1500] + "..." if len(simplified) > 1500 else simplified) or "(empty)")
    print()

    if audio_path:
        print("--- AUDIO ---")
        print("Saved to:", audio_path)
        print()

    # Optional: generate quiz from simplified text
    if simplified.strip():
        print("--- QUIZ (from simplified text) ---")
        quiz = pipeline.generate_quiz(simplified)
        for i, q in enumerate(quiz[:3], 1):
            print(f"{i}. {q.get('question', '')}")
            for opt in q.get("options", []):
                print(f"   - {opt}")
            print(f"   Answer: {q.get('answer', '')}")
            print()
        if not quiz:
            print("(No quiz generated)")

    print("Done.")


if __name__ == "__main__":
    main()
