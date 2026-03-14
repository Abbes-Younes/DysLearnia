# FastAPI backend – Dyslernia learning companion for dyslexic students
import os
import tempfile
import uuid
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Run from project root with: PYTHONPATH=backend uvicorn backend.app:app --reload
# Or from backend folder: uvicorn app:app --reload  (and use from agents...)
import sys
_backend = Path(__file__).resolve().parent
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

from agents.orchestrator import pipeline

app = FastAPI(
    title="Dyslernia API",
    description="AI learning companion for dyslexic students: OCR, simplify, quiz, hints, audio.",
)

# In-memory session store (use Redis/DB in production)
_sessions: dict[str, dict] = {}
# Where to store uploaded files and generated audio
UPLOAD_DIR = Path(tempfile.gettempdir()) / "dyslernia"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class SimplifyRequest(BaseModel):
    text: str


class HintRequest(BaseModel):
    question: str
    student_answer: str | None = None


class QuizRequest(BaseModel):
    text: str | None = None
    session_id: str | None = None


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/upload-course")
async def upload_course(file: UploadFile = File(...)):
    """
    Upload a course PDF (or image). Runs OCR → simplify → audio.
    Returns session_id, raw_text, simplified_text, and audio_url.
    """
    if not file.filename:
        raise HTTPException(400, "Missing filename")
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".pdf", ".png", ".jpg", ".jpeg"]:
        raise HTTPException(400, "Only PDF and images are supported")

    session_id = str(uuid.uuid4())
    path = UPLOAD_DIR / f"{session_id}{ext}"
    try:
        content = await file.read()
        path.write_bytes(content)
    except Exception as e:
        raise HTTPException(500, f"Failed to save file: {e}")

    try:
        result = pipeline.process_course(file_path=str(path))
    except Exception as e:
        raise HTTPException(500, f"Pipeline error: {e}")

    if result.get("error"):
        raise HTTPException(500, result["error"])

    # Store in session for later quiz/hint
    _sessions[session_id] = {
        "raw_text": result.get("raw_text"),
        "simplified_text": result.get("simplified_text"),
        "audio_path": result.get("audio_path"),
    }

    audio_path = result.get("audio_path")
    return {
        "session_id": session_id,
        "raw_text": result.get("raw_text", ""),
        "simplified_text": result.get("simplified_text", ""),
        "audio_url": f"/api/audio/{session_id}" if audio_path else None,
    }


@app.get("/api/audio/{session_id}")
def get_session_audio(session_id: str):
    """Stream the generated audio for a session."""
    session = _sessions.get(session_id)
    if not session or not session.get("audio_path"):
        raise HTTPException(404, "Audio not found for this session")
    path = Path(session["audio_path"])
    if not path.exists():
        raise HTTPException(404, "Audio file not found")
    return FileResponse(path, media_type="audio/wav")


@app.post("/api/simplify")
def simplify(req: SimplifyRequest):
    """Simplify raw text for dyslexic readers."""
    try:
        simplified = pipeline.simplify_text(req.text)
        return {"simplified_text": simplified}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/hint")
def hint(req: HintRequest):
    """Get a gentle hint for a question (optional: student's attempt)."""
    try:
        hint_text = pipeline.generate_hint(
            req.question,
            req.student_answer,
        )
        return {"hint": hint_text}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/quiz")
def quiz(req: QuizRequest):
    """Generate a quiz. Use text directly or from session_id."""
    text = req.text
    if not text and req.session_id:
        session = _sessions.get(req.session_id)
        if session:
            text = session.get("simplified_text") or session.get("raw_text")
    if not (text or "").strip():
        raise HTTPException(400, "Provide text or session_id with prior upload")
    try:
        questions = pipeline.generate_quiz(text)
        return {"quiz": questions}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/gamification/update")
def gamification_update(points: int = 10):
    """Update progress and get new points/badge."""
    try:
        return pipeline.update_progress(points)
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/gamification/status")
def gamification_status():
    """Get current points and badge."""
    try:
        return pipeline.get_progress()
    except Exception as e:
        raise HTTPException(500, str(e))
