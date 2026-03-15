from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Form
import json as json_lib
from core.pipeline import run_pipeline, validate_pipeline
from api.schemas import (
    SimplifyRequest, SimplifyResponse,
    QuizRequest, QuizResponse,
    HintRequest, HintResponse,
    GamificationRequest, GamificationResponse,
    PDFUploadResponse,
)
from utils.pdf import extract_text_from_pdf, chunk_text

router = APIRouter()


# ── Full pipeline: PDF → OCR → all agents ───────────────────────

@router.post("/process-pdf")
async def process_pdf(
    request: Request,
    file: UploadFile = File(...),
    reading_level: str = Form("adult"),
):
    """
    Full pipeline in one call:
    Upload PDF → OCR every page → chunk text →
    run simplifier + quiz on first chunk → return everything
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files accepted.")

    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Step 1 — OCR every page
    try:
        full_text = extract_text_from_pdf(contents)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Step 2 — chunk into 1500-char blocks
    chunks = chunk_text(full_text, max_chars=1500)
    first_chunk = chunks[0] if chunks else full_text[:1500]

    # Step 3 — run simplifier on first chunk
    graph = request.app.state.graph
    simplified_result = graph.invoke({
        "text": first_chunk,
        "task": "simplify",
        "reading_level": reading_level,
    })

    # Step 4 — run quiz on first chunk
    quiz_result = graph.invoke({
        "text": first_chunk,
        "task": "quiz",
        "reading_level": reading_level,
    })

    return {
        "total_chunks": len(chunks),
        "chunks": chunks,
        "current_chunk": 0,
        "reading_level": reading_level,
        "simplified_text": simplified_result.get("simplified_text", ""),
        "quiz": quiz_result.get("quiz", []),
    }

@router.post("/run-pipeline")
async def run_pipeline_endpoint(
    request: Request,
    file: UploadFile = File(...),
    pipeline: str = Form(...),
    reading_level: str = Form("adult"),
    user_question: str = Form(""),
):
    """
    Modular pipeline endpoint.
    pipeline JSON format:
    {
      "nodes": ["simplify", "quiz"],
      "edges": [{"from": "simplify", "to": "quiz"}]
    }
    Agents run in the order defined by edges.
    Each agent output is automatically available to downstream agents.
    """
    # parse pipeline
    try:
        flow = json_lib.loads(pipeline)
        nodes = flow.get("nodes", [])
        edges = flow.get("edges", [])
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid pipeline JSON.")

    # validate agents
    from core.pipeline import validate_pipeline
    errors = validate_pipeline(nodes, edges)
    if errors:
        raise HTTPException(status_code=400, detail=errors)

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files accepted.")

    contents = await file.read()

    # OCR
    try:
        raw_text = extract_text_from_pdf(contents)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    chunks = chunk_text(raw_text, max_chars=1500)
    first_chunk = chunks[0] if chunks else raw_text[:1500]

    # build initial state
    initial_state = {
        "raw_text": first_chunk,
        "reading_level": reading_level,
        "user_question": user_question,
        "task": "",
    }

    # run the pipeline
    graph = request.app.state.graph
    try:
        final_state = run_pipeline(nodes, edges, initial_state, graph)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "agents_run": final_state.get("agents_run", []),
        "total_chunks": len(chunks),
        "simplified_text": final_state.get("simplified_text"),
        "quiz": final_state.get("quiz"),
        "hint": final_state.get("hint"),
        "gamification": final_state.get("gamification"),
    }
# ── Individual agent endpoints (still available) ─────────────────

@router.post("/upload-pdf", response_model=PDFUploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """Upload only — returns raw chunks, no agents called."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files accepted.")
    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    try:
        full_text = extract_text_from_pdf(contents)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
    chunks = chunk_text(full_text, max_chars=1500)
    return PDFUploadResponse(
        full_text=full_text,
        chunks=chunks,
        total_chunks=len(chunks)
    )


@router.post("/simplify", response_model=SimplifyResponse)
async def simplify(body: SimplifyRequest, request: Request):
    graph = request.app.state.graph
    result = graph.invoke({
        "text": body.text,
        "task": "simplify",
        "reading_level": body.reading_level,
    })
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
        raise HTTPException(
            status_code=500,
            detail=f"LLM returned invalid JSON: {result['quiz_error']}"
        )
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
        raise HTTPException(
            status_code=500,
            detail=f"LLM returned invalid JSON: {result['gamification_error']}"
        )
    data = result["gamification"]
    return GamificationResponse(
        message=data.get("message", ""),
        badge=data.get("badge", ""),
        next_challenge=data.get("next_challenge", ""),
    )


# ── Health check ──────────────────────────────────────────────────

@router.get("/health")
async def health():
    return {"status": "ok"}