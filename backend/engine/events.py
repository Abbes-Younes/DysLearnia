"""
engine/events.py — WebSocket progress event shapes for pipeline execution.

Events are streamed to the frontend as JSON so the canvas can show
idle → running → done / error transitions on each node in real time.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from typing import Any, Literal


@dataclass
class PipelineEvent:
    """
    A single progress update for one pipeline node.

    node_id: the React Flow node id
    status:  "pending" | "running" | "done" | "error"
    data:    serialised block outputs (when status=="done") or error string
    """

    node_id: str
    status: Literal["pending", "running", "done", "error"]
    data: Any = None  # list[dict] (serialised BlockData) or error str

    def to_json(self) -> str:
        return json.dumps(asdict(self))


def block_data_to_dict(bd_list: list) -> list[dict]:
    """Serialise a list of BlockData to JSON-safe dicts (drops raw binary)."""
    result = []
    for bd in bd_list:
        item: dict[str, Any] = {
            "text": bd.text,
            "mime_type": bd.mime_type,
            "metadata": bd.metadata,
            "source_chunks": bd.source_chunks,
            # Omit binary — too large for WS; client fetches via separate endpoint
            "has_binary": bd.binary is not None,
        }
        result.append(item)
    return result
