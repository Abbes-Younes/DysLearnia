from fastapi import APIRouter, UploadFile, File, HTTPException, Request

from api.schemas import (
    SimplifyRequest, SimplifyResponse,
    QuizRequest, QuizResponse,
    HintRequest, HintResponse,
    GamificationRequest, GamificationResponse,
    PDFUploadResponse,
)
from utils.pdf import extract_text_from_pdf, chunk_text

router = APIRouter()


# ── PDF Upload ───────────────────────────────────────────────────

@router.post("/upload-pdf", response_model=PDFUploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF. Returns extracted text and pre-chunked segments
    ready to be passed to any agent endpoint.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        full_text = extract_text_from_pdf(contents)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not parse PDF: {e}")

    if not full_text.strip():
        raise HTTPException(status_code=422, detail="No text found in PDF. Is it a scanned image?")

    chunks = chunk_text(full_text, max_chars=1500)
    return PDFUploadResponse(full_text=full_text, chunks=chunks, total_chunks=len(chunks))


# ── Agent endpoints ──────────────────────────────────────────────

@router.post("/simplify", response_model=SimplifyResponse)
async def simplify(body: SimplifyRequest, request: Request):
    graph = request.app.state.graph
    result = graph.invoke({
        "text": body.text,
        "task": "simplify",
        "reading_level": body.reading_level,
    })
    
    if result.get("simplified_text_error"):
        raise HTTPException(status_code=500, detail=f"LLM returned invalid output: {result['simplified_text_error']}")

    return SimplifyResponse(simplified_text=result["simplified_text"])


@router.post("/quiz", response_model=QuizResponse)
async def generate_quiz(body: QuizRequest, request: Request):
    graph = request.app.state.graph
    result = graph.invoke({
        "text": body.text,
        "task": "quiz",
        "reading_level": body.reading_level,
    })

    if result.get("quiz_error"):
        raise HTTPException(status_code=500, detail=f"LLM returned invalid output: {result['quiz_error']}")

    return QuizResponse(quiz=result["quiz"])


@router.post("/hint", response_model=HintResponse)
async def get_hint(body: HintRequest, request: Request):
    graph = request.app.state.graph
    result = graph.invoke({
        "text": body.text,
        "task": "hint",
        "reading_level": body.reading_level,
        "user_question": body.user_question,
    })

    if result.get("hint_error"):
        raise HTTPException(status_code=500, detail=f"LLM returned invalid output: {result['hint_error']}")

    return HintResponse(hint=result["hint"])


@router.post("/gamification", response_model=GamificationResponse)
async def get_gamification(body: GamificationRequest, request: Request):
    graph = request.app.state.graph
    result = graph.invoke({
        "text": "",
        "task": "gamify",
        "reading_level": body.reading_level,
        "progress": {
            "score": body.score,
            "total": body.total,
            "streak": body.streak,
            "age_group": body.reading_level,
        },
    })

    if result.get("gamification_error"):
        raise HTTPException(status_code=500, detail=f"LLM returned invalid output: {result['gamification_error']}")

    gamification = result["gamification"]
    return GamificationResponse(
        message=gamification.message,
        badge=gamification.badge,
        next_challenge=gamification.next_challenge,
    )


# ── Health check ─────────────────────────────────────────────────

@router.get("/health")
async def health():
    return {"status": "ok"}
