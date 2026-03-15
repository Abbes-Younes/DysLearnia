"""
tests/test_validator.py — Unit tests for the pipeline edge validator.
"""
import pytest

import blocks  # noqa: F401 — register all blocks before tests run
from engine.validator import validate_edge, validate_pipeline, COMPATIBILITY


# ── validate_edge ─────────────────────────────────────────────────────────────

def test_text_can_connect_to_summarizer():
    assert validate_edge("text", "summarizer") is True


def test_text_can_connect_to_quiz_builder():
    assert validate_edge("text", "quiz_builder") is True


def test_text_can_connect_to_dyslexia_font():
    assert validate_edge("text", "dyslexia_font") is True


def test_text_can_connect_to_pdf_unifier():
    assert validate_edge("text", "pdf_unifier") is True


def test_binary_png_connects_to_pdf_unifier():
    assert validate_edge("binary/png", "pdf_unifier") is True


def test_binary_png_connects_to_video_unifier():
    assert validate_edge("binary/png", "video_unifier") is True


def test_binary_wav_connects_to_audio_unifier():
    assert validate_edge("binary/wav", "audio_unifier") is True


def test_binary_wav_connects_to_video_unifier():
    assert validate_edge("binary/wav", "video_unifier") is True


def test_binary_png_does_not_connect_to_summarizer():
    assert validate_edge("binary/png", "summarizer") is False


def test_binary_wav_does_not_connect_to_summarizer():
    assert validate_edge("binary/wav", "summarizer") is False


def test_unknown_output_type_returns_false():
    assert validate_edge("unknown/type", "summarizer") is False


def test_text_does_not_connect_to_video_unifier():
    # video_unifier only accepts binary/png and binary/wav, not text
    assert validate_edge("text", "video_unifier") is False


# ── validate_pipeline ─────────────────────────────────────────────────────────

def test_valid_pipeline_returns_no_errors():
    nodes = [
        {"id": "n1", "type": "course_input"},
        {"id": "n2", "type": "summarizer"},
    ]
    edges = [{"source": "n1", "target": "n2"}]
    errors = validate_pipeline(nodes, edges)
    assert errors == []


def test_invalid_edge_type_returns_error():
    nodes = [
        {"id": "n1", "type": "tts"},       # outputs binary/wav
        {"id": "n2", "type": "summarizer"},  # expects text
    ]
    edges = [{"source": "n1", "target": "n2"}]
    errors = validate_pipeline(nodes, edges)
    assert len(errors) >= 1
    assert any("summarizer" in e for e in errors)


def test_unknown_source_node_returns_error():
    nodes = [{"id": "n2", "type": "summarizer"}]
    edges = [{"source": "missing_node", "target": "n2"}]
    errors = validate_pipeline(nodes, edges)
    assert any("missing_node" in e for e in errors)


def test_unknown_target_node_returns_error():
    nodes = [{"id": "n1", "type": "summarizer"}]
    edges = [{"source": "n1", "target": "missing_node"}]
    errors = validate_pipeline(nodes, edges)
    assert any("missing_node" in e for e in errors)


def test_unknown_block_type_returns_error():
    nodes = [
        {"id": "n1", "type": "no_such_block"},
        {"id": "n2", "type": "summarizer"},
    ]
    edges = [{"source": "n1", "target": "n2"}]
    errors = validate_pipeline(nodes, edges)
    assert any("no_such_block" in e for e in errors)


def test_empty_pipeline_is_valid():
    errors = validate_pipeline([], [])
    assert errors == []


def test_valid_full_pipeline():
    """course_input → summarizer → dyslexia_font → pdf_unifier"""
    nodes = [
        {"id": "n1", "type": "course_input"},
        {"id": "n2", "type": "summarizer"},
        {"id": "n3", "type": "dyslexia_font"},
        {"id": "n4", "type": "pdf_unifier"},
    ]
    edges = [
        {"source": "n1", "target": "n2"},
        {"source": "n2", "target": "n3"},
        {"source": "n3", "target": "n4"},
    ]
    errors = validate_pipeline(nodes, edges)
    assert errors == []


def test_valid_pipeline_with_data_field():
    """Block type stored in node['data']['block_type']."""
    nodes = [
        {"id": "n1", "data": {"block_type": "course_input"}},
        {"id": "n2", "data": {"block_type": "summarizer"}},
    ]
    edges = [{"source": "n1", "target": "n2"}]
    errors = validate_pipeline(nodes, edges)
    assert errors == []
