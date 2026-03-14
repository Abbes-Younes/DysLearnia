from pydantic import BaseModel, Field
from typing import Optional, List, Dict


# ── Request bodies ──────────────────────────────────────────────

class SimplifyRequest(BaseModel):
    text: str = Field(..., min_length=10, description="Text extracted from PDF")
    reading_level: str = Field("adult", pattern="^(child|teen|adult)$")


class QuizRequest(BaseModel):
    text: str = Field(..., min_length=10)
    reading_level: str = Field("adult", pattern="^(child|teen|adult)$")


class HintRequest(BaseModel):
    text: str = Field(..., min_length=10, description="Course text as context")
    user_question: str = Field(..., min_length=3)
    reading_level: str = Field("adult", pattern="^(child|teen|adult)$")


class GamificationRequest(BaseModel):
    score: int = Field(..., ge=0)
    total: int = Field(..., ge=0)
    streak: int = Field(1, ge=1)
    reading_level: str = Field("adult", pattern="^(child|teen|adult)$")


# ── Response bodies ─────────────────────────────────────────────

class SimplifyResponse(BaseModel):
    simplified_text: str


class QuizQuestion(BaseModel):
    question: str
    options: Dict[str, str]
    answer: str
    explanation: str


class QuizResponse(BaseModel):
    quiz: List[QuizQuestion]
    error: Optional[str] = None


class HintResponse(BaseModel):
    hint: str


class GamificationResponse(BaseModel):
    message: str
    badge: str
    next_challenge: str
    error: Optional[str] = None


# ── PDF upload response ─────────────────────────────────────────

class PDFUploadResponse(BaseModel):
    full_text: str
    chunks: List[str]
    total_chunks: int
