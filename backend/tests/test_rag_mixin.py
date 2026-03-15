"""
tests/test_rag_mixin.py — Unit tests for RAGMixin confidence scoring
and prompt grounding (no Qdrant connection required).
"""
import pytest

from mixins.rag_mixin import RAGMixin


class _ConcreteRAG(RAGMixin):
    """Minimal concrete class to test RAGMixin methods."""
    pass


@pytest.fixture
def mixin():
    return _ConcreteRAG()


# ── _confidence_score ─────────────────────────────────────────────────────────

def test_confidence_no_hedges(mixin):
    text = "The mitochondria is the powerhouse of the cell."
    score = mixin._confidence_score(text)
    assert score == 1.0


def test_confidence_single_hedge(mixin):
    text = "This typically happens when the cell divides."
    score = mixin._confidence_score(text)
    assert score < 1.0


def test_confidence_many_hedges(mixin):
    text = (
        "I think this might generally be correct, "
        "but it could possibly be different. "
        "Perhaps it typically works this way."
    )
    score = mixin._confidence_score(text)
    assert score <= 0.5


def test_confidence_empty_string(mixin):
    assert mixin._confidence_score("") == 0.0


def test_confidence_case_insensitive(mixin):
    text = "TYPICALLY this is the case."
    score = mixin._confidence_score(text)
    assert score < 1.0


def test_confidence_score_floor_zero(mixin):
    # 11+ hedges should floor at 0.0
    hedges = " ".join(["typically"] * 15)
    score = mixin._confidence_score(hedges)
    assert score == 0.0


# ── _grounded_prompt ──────────────────────────────────────────────────────────

def test_grounded_prompt_no_chunks(mixin):
    result = mixin._grounded_prompt("summarise this", [])
    assert result == "summarise this"


def test_grounded_prompt_with_chunks(mixin):
    chunks = ["Chunk A content.", "Chunk B content."]
    result = mixin._grounded_prompt("summarise this", chunks)
    assert "Chunk A content." in result
    assert "Chunk B content." in result
    assert "ONLY" in result
    assert "INSUFFICIENT CONTEXT" in result


def test_grounded_prompt_contains_task(mixin):
    result = mixin._grounded_prompt("explain osmosis", ["water moves through membranes"])
    assert "explain osmosis" in result


def test_grounded_prompt_chunks_separated(mixin):
    chunks = ["first", "second"]
    result = mixin._grounded_prompt("task", chunks)
    assert "---" in result  # separator between chunks
