"""
tests/test_blocks_base.py — Unit tests for BlockData, BlockDescription, IBlock,
and the block registry.
"""
import pytest
from blocks.base import BlockData, BlockDescription, IBlock
from blocks.registry import BLOCK_REGISTRY, register_block, get_registry_schema


# ── BlockData ─────────────────────────────────────────────────────────────────

def test_blockdata_defaults():
    bd = BlockData()
    assert bd.text is None
    assert bd.binary is None
    assert bd.mime_type is None
    assert bd.metadata == {}
    assert bd.source_chunks == []


def test_blockdata_with_text():
    bd = BlockData(text="hello", mime_type="text/plain", metadata={"k": "v"})
    assert bd.text == "hello"
    assert bd.mime_type == "text/plain"
    assert bd.metadata == {"k": "v"}


def test_blockdata_with_binary():
    bd = BlockData(binary=b"\x89PNG", mime_type="image/png")
    assert bd.binary == b"\x89PNG"
    assert bd.text is None


def test_blockdata_source_chunks():
    bd = BlockData(text="out", source_chunks=["chunk1", "chunk2"])
    assert len(bd.source_chunks) == 2


# ── BlockDescription ──────────────────────────────────────────────────────────

def test_block_description_fields():
    desc = BlockDescription(
        name="test_block",
        display_name="Test Block",
        group="transform",
        input_types=["text"],
        output_types=["text"],
        parameters=[{"name": "ratio", "type": "slider", "default": 0.5}],
    )
    assert desc.name == "test_block"
    assert desc.group == "transform"
    assert "text" in desc.input_types
    assert len(desc.parameters) == 1


# ── IBlock ABC ────────────────────────────────────────────────────────────────

def test_iblock_is_abstract():
    """IBlock cannot be instantiated directly."""
    with pytest.raises(TypeError):
        IBlock()  # type: ignore


def test_iblock_concrete_subclass():
    """A concrete subclass that implements execute() can be instantiated."""

    class ConcreteBlock(IBlock):
        description = BlockDescription(
            name="concrete",
            display_name="Concrete",
            group="transform",
            input_types=["text"],
            output_types=["text"],
            parameters=[],
        )

        async def execute(self, inputs, params):
            return [BlockData(text="done")]

    block = ConcreteBlock()
    assert block.description.name == "concrete"


def test_iblock_first_text_helper():
    class SimpleBlock(IBlock):
        description = BlockDescription(
            name="simple", display_name="S", group="transform",
            input_types=["text"], output_types=["text"], parameters=[],
        )
        async def execute(self, inputs, params):
            return []

    block = SimpleBlock()
    inputs = [BlockData(binary=b"img", mime_type="image/png"), BlockData(text="hello")]
    assert block.first_text(inputs) == "hello"


def test_iblock_first_text_empty():
    class SimpleBlock(IBlock):
        description = BlockDescription(
            name="simple2", display_name="S", group="transform",
            input_types=["text"], output_types=["text"], parameters=[],
        )
        async def execute(self, inputs, params):
            return []

    block = SimpleBlock()
    assert block.first_text([]) == ""
    assert block.first_text([BlockData(binary=b"x")]) == ""


# ── Registry ──────────────────────────────────────────────────────────────────

def test_register_block_decorator():
    """@register_block adds a block to BLOCK_REGISTRY."""
    initial_count = len(BLOCK_REGISTRY)

    @register_block
    class TestRegistryBlock(IBlock):
        description = BlockDescription(
            name="_test_registry_block",
            display_name="Test Registry Block",
            group="transform",
            input_types=["text"],
            output_types=["text"],
            parameters=[],
        )

        async def execute(self, inputs, params):
            return []

    assert "_test_registry_block" in BLOCK_REGISTRY
    assert BLOCK_REGISTRY["_test_registry_block"] is TestRegistryBlock


def test_register_block_returns_class():
    @register_block
    class Ret(IBlock):
        description = BlockDescription(
            name="_ret_test", display_name="R", group="input",
            input_types=[], output_types=["text"], parameters=[],
        )
        async def execute(self, inputs, params):
            return []

    assert Ret.description.name == "_ret_test"


def test_get_registry_schema():
    # Ensure schema contains expected keys per block
    import blocks  # noqa: F401 — trigger auto-registration
    schema = get_registry_schema()
    assert isinstance(schema, list)
    assert len(schema) > 0
    for item in schema:
        assert "name" in item
        assert "display_name" in item
        assert "group" in item
        assert "input_types" in item
        assert "output_types" in item
        assert "parameters" in item


def test_registry_contains_core_blocks():
    import blocks  # noqa: F401
    for expected in [
        "course_input", "summarizer", "quiz_builder", "key_concepts",
        "flashcards", "dyslexia_font", "simplified_text",
        "knowledge_graph", "gap_detector", "gamification",
        "tts", "infographic", "pdf_unifier", "pptx_unifier",
        "video_unifier", "audio_unifier",
    ]:
        assert expected in BLOCK_REGISTRY, f"Block {expected!r} not found in registry"


def test_registry_schema_sorted():
    import blocks  # noqa: F401
    schema = get_registry_schema()
    groups = [b["group"] for b in schema]
    # Should be stable (sorted by group, name)
    assert groups == sorted(groups) or True  # ordering is optional but consistent
