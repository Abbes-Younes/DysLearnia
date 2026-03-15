"""
tests/test_dyslexia_font.py — Unit tests for DyslexiaFontBlock.

No LLM required — pure HTML reformatter.
"""
import asyncio

import pytest

from blocks.base import BlockData
from blocks.transform.dyslexia_font import DyslexiaFontBlock


@pytest.fixture
def block():
    return DyslexiaFontBlock()


@pytest.mark.asyncio
async def test_outputs_html(block):
    inputs = [BlockData(text="Hello world. This is a test.")]
    results = await block.execute(inputs, {})
    assert len(results) == 1
    assert results[0].mime_type == "text/html"
    assert "<html" in results[0].text


@pytest.mark.asyncio
async def test_contains_opendyslexic_font(block):
    inputs = [BlockData(text="Test content for dyslexia font.")]
    results = await block.execute(inputs, {"font": "OpenDyslexic"})
    assert "OpenDyslexic" in results[0].text


@pytest.mark.asyncio
async def test_contains_text_content(block):
    inputs = [BlockData(text="Photosynthesis converts sunlight.")]
    results = await block.execute(inputs, {})
    assert "Photosynthesis" in results[0].text


@pytest.mark.asyncio
async def test_respects_bg_color_param(block):
    inputs = [BlockData(text="Some text")]
    results = await block.execute(inputs, {"bg_color": "#FF0000"})
    assert "#FF0000" in results[0].text


@pytest.mark.asyncio
async def test_respects_line_height_param(block):
    inputs = [BlockData(text="Some text")]
    results = await block.execute(inputs, {"line_height": 2.5})
    assert "2.5" in results[0].text


@pytest.mark.asyncio
async def test_empty_text_returns_error_metadata(block):
    results = await block.execute([], {})
    assert results[0].metadata.get("error") is not None


@pytest.mark.asyncio
async def test_xss_in_text_is_escaped(block):
    inputs = [BlockData(text='<script>alert("xss")</script>')]
    results = await block.execute(inputs, {})
    assert "<script>" not in results[0].text
    assert "&lt;script&gt;" in results[0].text


@pytest.mark.asyncio
async def test_multiline_text_produces_paragraphs(block):
    inputs = [BlockData(text="Para one.\n\nPara two.\n\nPara three.")]
    results = await block.execute(inputs, {})
    assert results[0].text.count("<p>") >= 3
