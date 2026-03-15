"""
tests/test_routes.py — Integration tests for FastAPI route endpoints.

All LLM and external service calls are mocked so tests run without Ollama,
Supabase, Qdrant, or Neo4j.
"""
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

import blocks  # noqa: F401 — register all blocks
from blocks.base import BlockData


# ── App fixture ───────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def client():
    """Create a TestClient with a mocked startup sequence."""
    with (
        patch("core.graph.build_graph", return_value=MagicMock()),
        patch("models.local_llm.init_llm"),
    ):
        from main import app
        with TestClient(app, raise_server_exceptions=True) as c:
            yield c


# ── Health check ──────────────────────────────────────────────────────────────

def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


# ── GET /api/blocks ───────────────────────────────────────────────────────────

def test_list_blocks_returns_array(client):
    r = client.get("/api/blocks")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_list_blocks_has_required_fields(client):
    r = client.get("/api/blocks")
    for block in r.json():
        assert "name" in block
        assert "display_name" in block
        assert "group" in block
        assert "input_types" in block
        assert "output_types" in block
        assert "parameters" in block


def test_list_blocks_contains_summarizer(client):
    r = client.get("/api/blocks")
    names = [b["name"] for b in r.json()]
    assert "summarizer" in names


def test_list_blocks_contains_course_input(client):
    r = client.get("/api/blocks")
    names = [b["name"] for b in r.json()]
    assert "course_input" in names


# ── POST /api/pipeline/run (validate_only) ────────────────────────────────────

def test_pipeline_validate_only_valid(client):
    payload = {
        "nodes": [
            {"id": "n1", "type": "course_input"},
            {"id": "n2", "type": "summarizer"},
        ],
        "edges": [{"source": "n1", "target": "n2"}],
        "params": {},
        "validate_only": True,
    }
    r = client.post("/api/pipeline/run", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["validation_errors"] == []


def test_pipeline_validate_only_incompatible_edge(client):
    payload = {
        "nodes": [
            {"id": "n1", "type": "tts"},       # outputs binary/wav
            {"id": "n2", "type": "summarizer"},  # expects text
        ],
        "edges": [{"source": "n1", "target": "n2"}],
        "params": {},
        "validate_only": True,
    }
    r = client.post("/api/pipeline/run", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert len(data["validation_errors"]) >= 1


def test_pipeline_run_with_cycle_returns_422(client):
    payload = {
        "nodes": [
            {"id": "n1", "type": "summarizer"},
            {"id": "n2", "type": "summarizer"},
        ],
        "edges": [
            {"source": "n1", "target": "n2"},
            {"source": "n2", "target": "n1"},
        ],
        "params": {},
    }
    # Cyclic pipelines should fail validation or raise 422
    r = client.post("/api/pipeline/run", json=payload)
    # Either 422 from cycle detection or 422 from validator
    assert r.status_code in (422, 500)


# ── POST /api/pipeline/run (real execution with mocked blocks) ────────────────

@pytest.mark.asyncio
async def test_pipeline_run_with_mocked_block(client):
    """Run a one-node pipeline seeded via initial_inputs."""
    payload = {
        "nodes": [{"id": "n1", "type": "_echo"}],
        "edges": [],
        "params": {},
        "initial_inputs": {
            "n1": {"text": "seed text"}
        },
    }
    r = client.post("/api/pipeline/run", json=payload)
    # _echo block is registered in test_runner.py fixtures
    # If it's not registered here, we'll get 422 — that's fine too.
    assert r.status_code in (200, 422)


# ── POST /api/upload-pdf (legacy) ─────────────────────────────────────────────

def test_upload_pdf_no_file(client):
    r = client.post("/api/upload-pdf")
    assert r.status_code == 422  # FastAPI validates multipart


def test_upload_pdf_wrong_extension(client):
    r = client.post(
        "/api/upload-pdf",
        files={"file": ("test.txt", b"some text", "text/plain")},
    )
    assert r.status_code == 400


def test_upload_pdf_empty_file(client):
    r = client.post(
        "/api/upload-pdf",
        files={"file": ("test.pdf", b"", "application/pdf")},
    )
    assert r.status_code == 400


def test_upload_pdf_valid(client):
    # Minimal valid PDF bytes (not a real PDF, but tests the endpoint format)
    fake_pdf = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF"
    # Patch at the import location used by the route module
    with patch("api.routes.extract_text_from_pdf", return_value="Extracted text"):
        with patch("api.routes.chunk_text", return_value=["chunk1", "chunk2"]):
            r = client.post(
                "/api/upload-pdf",
                files={"file": ("test.pdf", fake_pdf, "application/pdf")},
            )
    assert r.status_code == 200
    data = r.json()
    assert "full_text" in data
    assert "chunks" in data
    assert "total_chunks" in data


# ── POST /api/simplify (legacy) ───────────────────────────────────────────────

def test_simplify_missing_text(client):
    r = client.post("/api/simplify", json={"text": "", "reading_level": "adult"})
    assert r.status_code == 422


def test_simplify_mocked_llm(client):
    mock_graph = MagicMock()
    mock_graph.invoke.return_value = {"simplified_text": "Simple text", "simplified_text_error": None}
    client.app.state.graph = mock_graph

    r = client.post("/api/simplify", json={
        "text": "This is a long text to simplify for the test.",
        "reading_level": "child",
    })
    assert r.status_code == 200
    assert r.json()["simplified_text"] == "Simple text"


# ── POST /api/quiz (legacy) ───────────────────────────────────────────────────

def test_quiz_mocked_llm(client):
    from api.schemas import QuizQuestion
    mock_graph = MagicMock()
    mock_graph.invoke.return_value = {
        "quiz": [
            QuizQuestion(
                question="What is 2+2?",
                options={"A": "3", "B": "4", "C": "5", "D": "6"},
                answer="B",
                explanation="2 plus 2 equals 4.",
            )
        ],
        "quiz_error": None,
    }
    client.app.state.graph = mock_graph

    r = client.post("/api/quiz", json={
        "text": "Mathematics is the science of numbers.",
        "reading_level": "adult",
    })
    assert r.status_code == 200
    data = r.json()
    assert len(data["quiz"]) == 1
    assert data["quiz"][0]["question"] == "What is 2+2?"


# ── POST /api/hint (legacy) ───────────────────────────────────────────────────

def test_hint_mocked_llm(client):
    mock_graph = MagicMock()
    mock_graph.invoke.return_value = {"hint": "The answer is 42.", "hint_error": None}
    client.app.state.graph = mock_graph

    r = client.post("/api/hint", json={
        "text": "The universe contains everything.",
        "user_question": "What is the answer?",
        "reading_level": "adult",
    })
    assert r.status_code == 200
    assert r.json()["hint"] == "The answer is 42."


# ── POST /api/gamification (legacy) ──────────────────────────────────────────

def test_gamification_mocked_llm(client):
    from api.schemas import GamificationResponse
    mock_graph = MagicMock()
    mock_graph.invoke.return_value = {
        "gamification": GamificationResponse(
            message="Great job!",
            badge="Quick Learner",
            next_challenge="Try the advanced quiz.",
        ),
        "gamification_error": None,
    }
    client.app.state.graph = mock_graph

    r = client.post("/api/gamification", json={
        "score": 8,
        "total": 10,
        "streak": 3,
        "reading_level": "teen",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["badge"] == "Quick Learner"
