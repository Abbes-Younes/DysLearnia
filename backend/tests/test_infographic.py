"""
tests/test_infographic.py — Unit tests for InfographicBlock.

Requires Pillow. Tests are skipped if Pillow is not installed.
"""
import pytest

pytest.importorskip("PIL", reason="Pillow not installed")

from blocks.base import BlockData
from blocks.transform.infographic import InfographicBlock


@pytest.fixture
def block():
    return InfographicBlock()


@pytest.mark.asyncio
async def test_outputs_png(block):
    inputs = [BlockData(text="Key concept: photosynthesis uses light energy.")]
    results = await block.execute(inputs, {})
    assert len(results) == 1
    assert results[0].mime_type == "image/png"
    assert results[0].binary is not None
    # PNG header magic bytes
    assert results[0].binary[:4] == b"\x89PNG"


@pytest.mark.asyncio
async def test_empty_input_returns_error(block):
    results = await block.execute([], {})
    assert results[0].metadata.get("error") is not None


@pytest.mark.asyncio
async def test_metadata_contains_dimensions(block):
    inputs = [BlockData(text="Some content here.")]
    results = await block.execute(inputs, {})
    meta = results[0].metadata
    assert "width" in meta
    assert "height" in meta


@pytest.mark.asyncio
async def test_dark_theme(block):
    inputs = [BlockData(text="Dark theme test content.")]
    results = await block.execute(inputs, {"theme": "dark"})
    assert results[0].binary is not None
    assert results[0].metadata.get("theme") == "dark"
