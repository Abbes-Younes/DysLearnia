"""
tests/test_runner.py — Unit tests for PipelineRunner (topological sort,
input collection, terminal output detection, and full execution with mocked blocks).
"""
import asyncio

import pytest

from blocks.base import BlockData, BlockDescription, IBlock
from blocks.registry import register_block, BLOCK_REGISTRY
from engine.runner import PipelineRunner


# ── Fixture blocks ────────────────────────────────────────────────────────────

@register_block
class _EchoBlock(IBlock):
    """Returns inputs unchanged — useful for testing data flow."""
    description = BlockDescription(
        name="_echo", display_name="Echo", group="transform",
        input_types=["text"], output_types=["text"], parameters=[],
    )

    async def execute(self, inputs, params):
        if inputs:
            return inputs
        return [BlockData(text="echo_default")]


@register_block
class _UpperBlock(IBlock):
    """Uppercases the first text input."""
    description = BlockDescription(
        name="_upper", display_name="Upper", group="transform",
        input_types=["text"], output_types=["text"], parameters=[],
    )

    async def execute(self, inputs, params):
        text = self.first_text(inputs)
        return [BlockData(text=text.upper())]


@register_block
class _FailBlock(IBlock):
    """Always raises an error — tests error propagation."""
    description = BlockDescription(
        name="_fail", display_name="Fail", group="transform",
        input_types=["text"], output_types=["text"], parameters=[],
    )

    async def execute(self, inputs, params):
        raise ValueError("Intentional failure")


# ── Topological sort ──────────────────────────────────────────────────────────

def test_topo_single_node():
    runner = PipelineRunner(
        nodes=[{"id": "n1", "type": "_echo"}],
        edges=[],
    )
    order = runner._topological_sort()
    assert order == ["n1"]


def test_topo_linear_chain():
    runner = PipelineRunner(
        nodes=[
            {"id": "n1", "type": "_echo"},
            {"id": "n2", "type": "_upper"},
            {"id": "n3", "type": "_echo"},
        ],
        edges=[
            {"source": "n1", "target": "n2"},
            {"source": "n2", "target": "n3"},
        ],
    )
    order = runner._topological_sort()
    assert order.index("n1") < order.index("n2")
    assert order.index("n2") < order.index("n3")


def test_topo_diamond_shape():
    """Diamond: n1 → n2, n1 → n3, n2 → n4, n3 → n4."""
    runner = PipelineRunner(
        nodes=[
            {"id": "n1", "type": "_echo"},
            {"id": "n2", "type": "_upper"},
            {"id": "n3", "type": "_echo"},
            {"id": "n4", "type": "_echo"},
        ],
        edges=[
            {"source": "n1", "target": "n2"},
            {"source": "n1", "target": "n3"},
            {"source": "n2", "target": "n4"},
            {"source": "n3", "target": "n4"},
        ],
    )
    order = runner._topological_sort()
    assert order.index("n1") < order.index("n2")
    assert order.index("n1") < order.index("n3")
    assert order.index("n2") < order.index("n4")
    assert order.index("n3") < order.index("n4")


def test_topo_cycle_raises():
    """A cyclic pipeline raises ValueError."""
    runner = PipelineRunner(
        nodes=[
            {"id": "n1", "type": "_echo"},
            {"id": "n2", "type": "_echo"},
        ],
        edges=[
            {"source": "n1", "target": "n2"},
            {"source": "n2", "target": "n1"},
        ],
    )
    with pytest.raises(ValueError, match="cycle"):
        runner._topological_sort()


# ── Input collection ──────────────────────────────────────────────────────────

def test_collect_inputs_empty():
    runner = PipelineRunner(
        nodes=[{"id": "n1", "type": "_echo"}],
        edges=[],
    )
    runner.run_data["n1"] = [BlockData(text="hi")]
    # n2 has no upstream
    runner.nodes["n2"] = {"id": "n2", "type": "_echo"}
    assert runner._collect_inputs("n1") == []


def test_collect_inputs_single_upstream():
    runner = PipelineRunner(
        nodes=[{"id": "n1", "type": "_echo"}, {"id": "n2", "type": "_upper"}],
        edges=[{"source": "n1", "target": "n2"}],
    )
    runner.run_data["n1"] = [BlockData(text="hello")]
    inputs = runner._collect_inputs("n2")
    assert len(inputs) == 1
    assert inputs[0].text == "hello"


def test_collect_inputs_multiple_upstream():
    runner = PipelineRunner(
        nodes=[
            {"id": "n1", "type": "_echo"},
            {"id": "n2", "type": "_echo"},
            {"id": "n3", "type": "_echo"},
        ],
        edges=[
            {"source": "n1", "target": "n3"},
            {"source": "n2", "target": "n3"},
        ],
    )
    runner.run_data["n1"] = [BlockData(text="from_n1")]
    runner.run_data["n2"] = [BlockData(text="from_n2")]
    inputs = runner._collect_inputs("n3")
    texts = {bd.text for bd in inputs}
    assert texts == {"from_n1", "from_n2"}


# ── Terminal outputs ──────────────────────────────────────────────────────────

def test_terminal_outputs_single():
    runner = PipelineRunner(
        nodes=[
            {"id": "n1", "type": "_echo"},
            {"id": "n2", "type": "_upper"},
        ],
        edges=[{"source": "n1", "target": "n2"}],
    )
    runner.run_data["n1"] = [BlockData(text="src")]
    runner.run_data["n2"] = [BlockData(text="DST")]
    terminals = runner._terminal_outputs()
    assert "n2" in terminals
    assert "n1" not in terminals


def test_terminal_outputs_multiple_sinks():
    runner = PipelineRunner(
        nodes=[
            {"id": "n1", "type": "_echo"},
            {"id": "n2", "type": "_echo"},
            {"id": "n3", "type": "_echo"},
        ],
        edges=[
            {"source": "n1", "target": "n2"},
            {"source": "n1", "target": "n3"},
        ],
    )
    runner.run_data = {"n1": [], "n2": [BlockData(text="2")], "n3": [BlockData(text="3")]}
    terminals = runner._terminal_outputs()
    assert set(terminals.keys()) == {"n2", "n3"}


# ── Full async execution ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_execute_single_node():
    runner = PipelineRunner(
        nodes=[{"id": "n1", "type": "_echo"}],
        edges=[],
    )
    runner.run_data["n1"] = []  # seed with empty — _echo returns default
    outputs = await runner.execute({})
    # Single-node pipeline: n1 is both source and terminal
    # Since we pre-seeded, _echo returns the pre-seeded empty list as inputs
    assert "n1" in outputs


@pytest.mark.asyncio
async def test_execute_linear_chain():
    runner = PipelineRunner(
        nodes=[
            {"id": "n1", "type": "_echo"},
            {"id": "n2", "type": "_upper"},
        ],
        edges=[{"source": "n1", "target": "n2"}],
    )
    # Seed n1 with known input
    runner.run_data["n1"] = [BlockData(text="hello")]
    outputs = await runner.execute({})
    assert "n2" in outputs
    assert outputs["n2"][0].text == "HELLO"


@pytest.mark.asyncio
async def test_execute_with_progress_callback():
    events = []

    async def progress_cb(node_id, status, data):
        events.append((node_id, status))

    runner = PipelineRunner(
        nodes=[{"id": "n1", "type": "_echo"}],
        edges=[],
    )
    runner.run_data["n1"] = []
    await runner.execute({}, progress_cb=progress_cb)

    assert ("n1", "running") in events
    assert ("n1", "done") in events


@pytest.mark.asyncio
async def test_execute_error_block_raises():
    runner = PipelineRunner(
        nodes=[{"id": "n1", "type": "_fail"}],
        edges=[],
    )
    with pytest.raises(RuntimeError, match="Intentional failure"):
        await runner.execute({})


@pytest.mark.asyncio
async def test_execute_error_fires_progress_callback():
    events = []

    async def progress_cb(node_id, status, data):
        events.append((node_id, status))

    runner = PipelineRunner(
        nodes=[{"id": "n1", "type": "_fail"}],
        edges=[],
    )
    with pytest.raises(RuntimeError):
        await runner.execute({}, progress_cb=progress_cb)

    assert ("n1", "error") in events


@pytest.mark.asyncio
async def test_execute_unknown_block_raises():
    runner = PipelineRunner(
        nodes=[{"id": "n1", "type": "no_such_block"}],
        edges=[],
    )
    with pytest.raises(ValueError, match="Unknown block type"):
        await runner.execute({})
