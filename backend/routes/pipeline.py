"""
routes/pipeline.py — Pipeline execution endpoints.

POST  /api/pipeline/run  — Synchronous execution, returns terminal outputs.
WS    /ws/pipeline/{run_id} — Streaming execution with live progress events.
"""
from __future__ import annotations

import json
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

router = APIRouter(tags=["Pipeline"])


# ── Request / Response schemas ────────────────────────────────────────────────

class NodeDef(BaseModel):
    id: str
    type: str  # block registry key
    data: dict[str, Any] = Field(default_factory=dict)


class EdgeDef(BaseModel):
    source: str
    target: str


class PipelineRunRequest(BaseModel):
    """
    A complete pipeline definition + per-node parameters.

    Example:
    ```json
    {
      "nodes": [
        {"id": "n1", "type": "course_input"},
        {"id": "n2", "type": "summarizer"},
        {"id": "n3", "type": "dyslexia_font"}
      ],
      "edges": [
        {"source": "n1", "target": "n2"},
        {"source": "n2", "target": "n3"}
      ],
      "params": {
        "n1": {"doc_id": "abc123"},
        "n2": {"ratio": 0.4, "style": "paragraph"},
        "n3": {"font": "OpenDyslexic"}
      },
      "initial_inputs": {
        "n1": {"text": "The mitochondria is the powerhouse..."}
      }
    }
    ```
    """

    nodes: list[NodeDef]
    edges: list[EdgeDef]
    params: dict[str, dict[str, Any]] = Field(default_factory=dict)
    initial_inputs: dict[str, dict[str, Any]] = Field(
        default_factory=dict,
        description="Pre-seeded BlockData for source nodes (e.g. pre-uploaded text)",
    )
    validate_only: bool = Field(
        False,
        description="If true, only validate the pipeline and return errors without running",
    )


class BlockDataOut(BaseModel):
    text: str | None = None
    mime_type: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    source_chunks: list[str] = Field(default_factory=list)
    has_binary: bool = False


class PipelineRunResponse(BaseModel):
    run_id: str
    outputs: dict[str, list[BlockDataOut]]
    validation_errors: list[str] = Field(default_factory=list)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _request_to_runner_nodes(nodes: list[NodeDef]) -> list[dict]:
    return [{"id": n.id, "type": n.type, "data": n.data} for n in nodes]


def _request_to_runner_edges(edges: list[EdgeDef]) -> list[dict]:
    return [{"source": e.source, "target": e.target} for e in edges]


def _seed_runner(runner, initial_inputs: dict[str, dict]) -> None:
    """Pre-populate run_data for source nodes from initial_inputs."""
    from blocks.base import BlockData
    for node_id, bd_kwargs in initial_inputs.items():
        bd = BlockData(**{k: v for k, v in bd_kwargs.items()
                         if k in {"text", "binary", "mime_type", "metadata", "source_chunks"}})
        runner.run_data[node_id] = [bd]


def _serialise_outputs(outputs: dict) -> dict[str, list[BlockDataOut]]:
    result = {}
    for node_id, bd_list in outputs.items():
        result[node_id] = [
            BlockDataOut(
                text=bd.text,
                mime_type=bd.mime_type,
                metadata=bd.metadata,
                source_chunks=bd.source_chunks,
                has_binary=bd.binary is not None,
            )
            for bd in bd_list
        ]
    return result


# ── REST endpoint ─────────────────────────────────────────────────────────────

@router.post(
    "/pipeline/run",
    response_model=PipelineRunResponse,
    summary="Execute a pipeline synchronously",
)
async def run_pipeline(body: PipelineRunRequest):
    """
    Execute a pipeline and return the terminal node outputs.

    Binary outputs (audio, PDF, images) are indicated by `has_binary: true`.
    Fetch the actual bytes via `GET /api/pipeline/{run_id}/output/{node_id}`.
    """
    from engine.runner import PipelineRunner
    from engine.validator import validate_pipeline

    run_nodes = _request_to_runner_nodes(body.nodes)
    run_edges = _request_to_runner_edges(body.edges)

    # Validate first
    errors = validate_pipeline(run_nodes, run_edges)

    if body.validate_only:
        return PipelineRunResponse(
            run_id="",
            outputs={},
            validation_errors=errors,
        )

    if errors:
        raise HTTPException(
            status_code=422,
            detail={"message": "Pipeline validation failed", "errors": errors},
        )

    run_id = str(uuid.uuid4())
    runner = PipelineRunner(run_nodes, run_edges)
    _seed_runner(runner, body.initial_inputs)

    try:
        outputs = await runner.execute(body.params)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    # Store binary outputs in-memory keyed by run_id (simple in-process cache)
    _binary_store[run_id] = {
        node_id: bd_list for node_id, bd_list in runner.run_data.items()
    }

    return PipelineRunResponse(
        run_id=run_id,
        outputs=_serialise_outputs(outputs),
    )


# Simple in-process binary store (replaced by Supabase Storage in production)
_binary_store: dict[str, dict[str, list]] = {}


@router.get(
    "/pipeline/{run_id}/output/{node_id}",
    summary="Download binary output from a completed pipeline run",
    responses={
        200: {"description": "Raw binary file"},
        404: {"description": "Run or node not found"},
    },
)
async def get_binary_output(run_id: str, node_id: str):
    """
    Download the binary output (PDF / PPTX / MP4 / MP3 / PNG / WAV)
    for a specific node from a completed pipeline run.
    """
    from fastapi.responses import Response

    run_data = _binary_store.get(run_id)
    if run_data is None:
        raise HTTPException(status_code=404, detail=f"Run {run_id!r} not found")

    bd_list = run_data.get(node_id)
    if not bd_list:
        raise HTTPException(status_code=404, detail=f"Node {node_id!r} not found in run")

    for bd in bd_list:
        if bd.binary:
            filename = bd.metadata.get("filename", f"{node_id}_output")
            return Response(
                content=bd.binary,
                media_type=bd.mime_type or "application/octet-stream",
                headers={"Content-Disposition": f'attachment; filename="{filename}"'},
            )

    raise HTTPException(status_code=404, detail="No binary output for this node")


# ── WebSocket endpoint ────────────────────────────────────────────────────────

@router.websocket("/ws/pipeline/{run_id}")
async def pipeline_ws(websocket: WebSocket, run_id: str):
    """
    WebSocket endpoint for streaming pipeline execution.

    The client sends a JSON pipeline definition (same shape as PipelineRunRequest).
    The server streams PipelineEvent JSON objects as each node transitions:
      {"node_id": "n1", "status": "running", "data": null}
      {"node_id": "n1", "status": "done",    "data": [{...BlockData...}]}
    On error:
      {"node_id": "n2", "status": "error",   "data": "error message"}
    On completion:
      {"node_id": null, "status": "complete", "data": null}
    """
    from engine.runner import PipelineRunner
    from engine.validator import validate_pipeline
    from engine.events import PipelineEvent, block_data_to_dict

    await websocket.accept()

    try:
        raw = await websocket.receive_text()
        body_data = json.loads(raw)

        nodes_raw = body_data.get("nodes", [])
        edges_raw = body_data.get("edges", [])
        params = body_data.get("params", {})
        initial_inputs = body_data.get("initial_inputs", {})

        run_nodes = [{"id": n["id"], "type": n["type"], "data": n.get("data", {})}
                     for n in nodes_raw]
        run_edges = [{"source": e["source"], "target": e["target"]} for e in edges_raw]

        errors = validate_pipeline(run_nodes, run_edges)
        if errors:
            await websocket.send_text(json.dumps({
                "node_id": None, "status": "validation_error", "data": errors
            }))
            await websocket.close()
            return

        runner = PipelineRunner(run_nodes, run_edges)
        _seed_runner(runner, initial_inputs)

        async def progress_cb(node_id: str, status: str, bd_list):
            data = block_data_to_dict(bd_list) if bd_list is not None else None
            event = PipelineEvent(node_id=node_id, status=status, data=data)
            await websocket.send_text(event.to_json())

        try:
            await runner.execute(params, progress_cb=progress_cb)
        except (ValueError, RuntimeError) as exc:
            await websocket.send_text(json.dumps({
                "node_id": None, "status": "error", "data": str(exc)
            }))
            await websocket.close()
            return

        # Store binary outputs
        _binary_store[run_id] = runner.run_data

        await websocket.send_text(json.dumps({
            "node_id": None, "status": "complete", "data": None
        }))

    except WebSocketDisconnect:
        pass
    except Exception as exc:
        try:
            await websocket.send_text(json.dumps({
                "node_id": None, "status": "error", "data": str(exc)
            }))
        except Exception:
            pass
