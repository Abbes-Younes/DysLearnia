"""
routes/documents.py — Document upload and Qdrant indexing endpoint.

POST /api/documents/upload — accepts PDF/PPTX/video, extracts text,
                              indexes into Qdrant Cloud, returns doc_id + chunks.
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile, Header
from pydantic import BaseModel

router = APIRouter(tags=["Documents"])

_ACCEPTED_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "video/mp4",
    "video/quicktime",
    "video/x-matroska",
    "video/webm",
}


class DocumentUploadResponse(BaseModel):
    doc_id: str
    filename: str
    mime_type: str
    page_count: int
    chunk_count: int
    preview_text: str  # first 500 chars of extracted text


@router.post(
    "/documents/upload",
    response_model=DocumentUploadResponse,
    summary="Upload a course document and index it into Qdrant",
)
async def upload_document(
    file: UploadFile = File(...),
    authorization: str | None = Header(None),
):
    """
    Upload a course material file (PDF, PPTX, or video).

    - Extracts text (and slide/keyframe images for PDFs/videos).
    - Chunks text and indexes all chunks into Qdrant Cloud.
    - Returns a `doc_id` that downstream blocks use for RAG retrieval.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    # Determine MIME type
    mime = file.content_type or ""
    filename_lower = (file.filename or "").lower()
    if not mime or mime == "application/octet-stream":
        if filename_lower.endswith(".pdf"):
            mime = "application/pdf"
        elif filename_lower.endswith(".pptx"):
            mime = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        elif filename_lower.endswith((".mp4", ".mov", ".mkv", ".webm")):
            mime = "video/mp4"

    # Extract user ID for Qdrant payload
    from db.supabase import get_client as sb_client
    user_id = "anonymous"
    if sb_client() and authorization and authorization.startswith("Bearer "):
        try:
            token = authorization.removeprefix("Bearer ").strip()
            resp = sb_client().auth.get_user(token)
            if resp.user:
                user_id = resp.user.id
        except Exception:
            pass

    # Extract text via the CourseInputBlock logic
    from blocks.base import BlockData
    from blocks.inputs.course_input import CourseInputBlock

    block = CourseInputBlock()
    input_bd = BlockData(binary=contents, mime_type=mime, metadata={"user_id": user_id})

    try:
        results = await block.execute([input_bd], {"extract_images": False})
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Extraction failed: {exc}")

    if not results or not results[0].text:
        raise HTTPException(
            status_code=422,
            detail="No text could be extracted from the file.",
        )

    bd = results[0]
    doc_id = bd.metadata.get("doc_id", str(uuid.uuid4()))
    page_count = bd.metadata.get("page_count", 0)
    chunk_count = bd.metadata.get("chunk_count", 0)
    preview_text = (bd.text or "")[:500]

    return DocumentUploadResponse(
        doc_id=doc_id,
        filename=file.filename or "unknown",
        mime_type=mime,
        page_count=page_count,
        chunk_count=chunk_count,
        preview_text=preview_text,
    )
