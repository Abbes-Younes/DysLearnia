"""
engine/runner.py — PipelineRunner: topological execution with live WS events.

Accepts a pipeline definition (nodes + edges + params), executes blocks
in dependency order, and streams progress events via an optional callback.
Equivalent to n8n's WorkflowExecute but stripped to the educational domain.
"""
from __future__ import annotations

import asyncio
from collections import defaultdict, deque
from typing import Any, Awaitable, Callable

from blocks.base import BlockData


ProgressCallback = Callable[
    [str, str, list[BlockData] | None],
    Awaitable[None],
]


class PipelineRunner:
    """
    Execute a pipeline defined as a list of nodes and directed edges.

    Nodes are executed in topological (dependency) order.
    Progress events are emitted via `progress_cb` so the WebSocket route
    can forward them to the frontend in real time.
    """

    def __init__(self, nodes: list[dict], edges: list[dict]):
        """
        Args:
            nodes: List of node dicts, each with at minimum:
                   {"id": str, "type": str}  — type is the block registry key.
                   Data node fields can also live under "data": {"block_type": str}.
            edges: List of edge dicts: {"source": str, "target": str}.
        """
        self.nodes = {n["id"]: n for n in nodes}
        self.edges = edges
        self.run_data: dict[str, list[BlockData]] = {}
        # Pre-supplied inputs for source nodes (e.g. uploaded file bytes).
        # Checked in _collect_inputs when a node has no incoming edges.
        # Unlike run_data seeding, these are passed INTO block.execute() so
        # the block still runs (e.g. CourseInputBlock extracts text from binary).
        self.source_inputs: dict[str, list[BlockData]] = {}

    # ── Topological sort (Kahn's algorithm) ──────────────────────────────────

    def _topological_sort(self) -> list[str]:
        """
        Return node IDs in topological execution order.
        Raises ValueError if the pipeline contains a cycle.
        """
        in_degree: dict[str, int] = defaultdict(int)
        adj: dict[str, list[str]] = defaultdict(list)

        for node_id in self.nodes:
            in_degree[node_id]  # ensure all nodes appear in in_degree

        for edge in self.edges:
            src = edge["source"]
            tgt = edge["target"]
            adj[src].append(tgt)
            in_degree[tgt] += 1

        queue: deque[str] = deque(
            nid for nid in self.nodes if in_degree[nid] == 0
        )
        order: list[str] = []

        while queue:
            nid = queue.popleft()
            order.append(nid)
            for neighbor in adj[nid]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) != len(self.nodes):
            raise ValueError(
                "Pipeline contains a cycle — execution aborted. "
                "Ensure the pipeline is a directed acyclic graph (DAG)."
            )

        return order

    # ── Input collection ──────────────────────────────────────────────────────

    def _collect_inputs(self, node_id: str) -> list[BlockData]:
        """
        Gather all BlockData for a node's execute() call.
        For source nodes (no incoming edges), check source_inputs.
        """
        inputs: list[BlockData] = []
        for edge in self.edges:
            if edge["target"] == node_id:
                upstream_outputs = self.run_data.get(edge["source"], [])
                inputs.extend(upstream_outputs)
        if not inputs and node_id in self.source_inputs:
            inputs = self.source_inputs[node_id]
        return inputs

    # ── Terminal output nodes ────────────────────────────────────────────────

    def _terminal_outputs(self) -> dict[str, list[BlockData]]:
        """Return the run_data of nodes that have no outgoing edges."""
        nodes_with_outgoing = {e["source"] for e in self.edges}
        return {
            nid: data
            for nid, data in self.run_data.items()
            if nid not in nodes_with_outgoing
        }

    # ── Main execution entry point ────────────────────────────────────────────

    async def execute(
        self,
        params: dict[str, dict],
        progress_cb: ProgressCallback | None = None,
    ) -> dict[str, list[BlockData]]:
        """
        Execute the pipeline.

        Args:
            params: Mapping of node_id → {param_name: value}.
            progress_cb: Optional async callback receiving (node_id, status, data).

        Returns:
            Dict of terminal node outputs: {node_id: [BlockData]}.
        """
        from blocks.registry import BLOCK_REGISTRY

        order = self._topological_sort()

        for node_id in order:
            # Skip nodes whose outputs are already pre-seeded (initial_inputs / cache)
            if self.run_data.get(node_id):
                if progress_cb:
                    await progress_cb(node_id, "done", self.run_data[node_id])
                continue

            node = self.nodes[node_id]
            block_type = (
                node.get("type")
                or node.get("data", {}).get("block_type")
            )

            if block_type not in BLOCK_REGISTRY:
                raise ValueError(
                    f"Unknown block type {block_type!r} on node {node_id!r}. "
                    f"Available: {sorted(BLOCK_REGISTRY.keys())}"
                )

            block = BLOCK_REGISTRY[block_type]()
            node_params = params.get(node_id, {})
            inputs = self._collect_inputs(node_id)

            if progress_cb:
                await progress_cb(node_id, "running", None)

            try:
                result = await block.execute(inputs, node_params)
                self.run_data[node_id] = result
                if progress_cb:
                    await progress_cb(node_id, "done", result)

            except Exception as exc:
                if progress_cb:
                    await progress_cb(node_id, "error", None)
                raise RuntimeError(
                    f"Block {block_type!r} on node {node_id!r} raised: {exc}"
                ) from exc

        return self._terminal_outputs()
