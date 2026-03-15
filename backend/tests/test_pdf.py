import pytest
from utils.pdf import chunk_text

def test_chunk_text_basic():
    text = "Short paragraph 1.\n\nShort paragraph 2."
    chunks = chunk_text(text, max_chars=100)
    assert len(chunks) == 1
    assert chunks[0] == "Short paragraph 1.\n\nShort paragraph 2."

def test_chunk_text_split():
    text = "A" * 100 + "\n\n" + "B" * 100
    chunks = chunk_text(text, max_chars=150)
    assert len(chunks) == 2
    assert chunks[0] == "A" * 100
    assert chunks[1] == "B" * 100

def test_chunk_text_long_paragraph():
    text = "A" * 300
    chunks = chunk_text(text, max_chars=150)
    assert len(chunks) == 2
    assert chunks[0] == "A" * 150
    assert chunks[1] == "A" * 150
