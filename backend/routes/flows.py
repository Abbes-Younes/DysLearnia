"""
routes/flows.py — Flow persistence endpoints (Supabase-backed).

POST   /api/flows          — create or update a flow
GET    /api/flows           — list owned + public/template flows
GET    /api/flows/{id}      — load single flow
POST   /api/flows/{id}/fork — fork a flow (copies graph, new owner)
DELETE /api/flows/{id}      — delete a flow
PATCH  /api/flows/{id}/promote — teacher: promote to template
POST   /api/flows/{id}/comments — add a comment to a node
GET    /api/flows/{id}/comments — list comments on a flow
PATCH  /api/flows/{id}/comments/{comment_id} — resolve a comment
"""
from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel, Field

router = APIRouter(tags=["Flows"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class FlowGraph(BaseModel):
    nodes: list[dict[str, Any]]
    edges: list[dict[str, Any]]


class FlowUpsertRequest(BaseModel):
    id: str | None = None
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    graph: FlowGraph
    thumbnail: str | None = None  # base64 PNG canvas snapshot
    is_public: bool = False
    locked_params: dict[str, list[str]] = Field(default_factory=dict)


class CommentCreateRequest(BaseModel):
    node_id: str
    body: str = Field(..., min_length=1)
    author_role: str = Field("student", pattern="^(student|teacher)$")


# ── Auth helper ───────────────────────────────────────────────────────────────

def _get_supabase_client():
    from db.supabase import get_client
    client = get_client()
    if client is None:
        raise HTTPException(
            status_code=503,
            detail="Supabase not configured — set SUPABASE_URL and SUPABASE_SERVICE_KEY",
        )
    return client


def _get_user_id(authorization: str | None) -> str:
    """
    Extract user_id from Bearer token via Supabase.
    Falls back to anonymous in dev mode (no SUPABASE_URL set).
    """
    from db.supabase import get_client
    if get_client() is None:
        return "anonymous"
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.removeprefix("Bearer ").strip()
    try:
        from db.supabase import get_client as gc
        client = gc()
        resp = client.auth.get_user(token)
        if not resp.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return resp.user.id
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=401, detail=f"Auth error: {exc}")


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/flows", summary="Create or update a flow")
async def upsert_flow(
    body: FlowUpsertRequest,
    authorization: str | None = Header(None),
):
    """Upsert (create or update) a saved pipeline flow."""
    client = _get_supabase_client()
    user_id = _get_user_id(authorization)

    flow_id = body.id or str(uuid.uuid4())
    graph_dict = {"nodes": body.graph.nodes, "edges": body.graph.edges}

    data = {
        "id": flow_id,
        "owner_id": user_id,
        "title": body.title,
        "description": body.description,
        "graph": graph_dict,
        "thumbnail": body.thumbnail,
        "is_public": body.is_public,
        "locked_params": body.locked_params,
    }

    result = client.table("flows").upsert(data).execute()
    return {"id": flow_id, "data": result.data}


@router.get("/flows", summary="List owned and public/template flows")
async def list_flows(authorization: str | None = Header(None)):
    """List flows owned by the current user plus public/template flows."""
    client = _get_supabase_client()
    user_id = _get_user_id(authorization)

    result = (
        client.table("flows")
        .select("id,title,description,thumbnail,is_template,is_public,created_at,updated_at")
        .or_(f"owner_id.eq.{user_id},is_public.eq.true,is_template.eq.true")
        .order("updated_at", desc=True)
        .execute()
    )
    return {"flows": result.data}


@router.get("/flows/{flow_id}", summary="Load a single flow")
async def get_flow(flow_id: str, authorization: str | None = Header(None)):
    """Load a flow by ID. Must be owner or flow must be public/template."""
    client = _get_supabase_client()
    user_id = _get_user_id(authorization)

    result = (
        client.table("flows")
        .select("*")
        .eq("id", flow_id)
        .single()
        .execute()
    )
    flow = result.data
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")
    if flow["owner_id"] != user_id and not flow.get("is_public") and not flow.get("is_template"):
        raise HTTPException(status_code=403, detail="Access denied")
    return flow


@router.post("/flows/{flow_id}/fork", summary="Fork a flow")
async def fork_flow(flow_id: str, authorization: str | None = Header(None)):
    """Fork an existing flow — creates a new flow owned by the current user."""
    client = _get_supabase_client()
    user_id = _get_user_id(authorization)

    source = (
        client.table("flows")
        .select("*")
        .eq("id", flow_id)
        .single()
        .execute()
    ).data
    if not source:
        raise HTTPException(status_code=404, detail="Source flow not found")

    new_id = str(uuid.uuid4())
    forked = {
        "id": new_id,
        "owner_id": user_id,
        "title": f"{source['title']} (fork)",
        "description": source.get("description"),
        "graph": source.get("graph"),
        "thumbnail": source.get("thumbnail"),
        "is_public": False,
        "is_template": False,
        "forked_from": flow_id,
        "locked_params": source.get("locked_params", {}),
    }
    client.table("flows").insert(forked).execute()
    return {"id": new_id}


@router.delete("/flows/{flow_id}", summary="Delete a flow")
async def delete_flow(flow_id: str, authorization: str | None = Header(None)):
    """Delete a flow. Only the owner may delete."""
    client = _get_supabase_client()
    user_id = _get_user_id(authorization)

    flow = (
        client.table("flows").select("owner_id").eq("id", flow_id).single().execute()
    ).data
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")
    if flow["owner_id"] != user_id:
        raise HTTPException(status_code=403, detail="Only the owner may delete this flow")

    client.table("flows").delete().eq("id", flow_id).execute()
    return {"deleted": True}


@router.patch("/flows/{flow_id}/promote", summary="Promote flow to template (teacher only)")
async def promote_flow(
    flow_id: str,
    locked_params: dict[str, list[str]] | None = None,
    authorization: str | None = Header(None),
):
    """Mark a flow as a template. Only the owner may promote."""
    client = _get_supabase_client()
    user_id = _get_user_id(authorization)

    flow = (
        client.table("flows").select("owner_id").eq("id", flow_id).single().execute()
    ).data
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")
    if flow["owner_id"] != user_id:
        raise HTTPException(status_code=403, detail="Only the owner may promote this flow")

    update = {"is_template": True}
    if locked_params is not None:
        update["locked_params"] = locked_params

    client.table("flows").update(update).eq("id", flow_id).execute()
    return {"promoted": True}


# ── Comments ──────────────────────────────────────────────────────────────────

@router.post("/flows/{flow_id}/comments", summary="Add a comment to a node")
async def add_comment(
    flow_id: str,
    body: CommentCreateRequest,
    authorization: str | None = Header(None),
):
    client = _get_supabase_client()
    user_id = _get_user_id(authorization)
    comment = {
        "id": str(uuid.uuid4()),
        "flow_id": flow_id,
        "node_id": body.node_id,
        "author_id": user_id,
        "author_role": body.author_role,
        "body": body.body,
        "resolved": False,
    }
    result = client.table("node_comments").insert(comment).execute()
    return {"comment": result.data}


@router.get("/flows/{flow_id}/comments", summary="List comments on a flow")
async def list_comments(flow_id: str, authorization: str | None = Header(None)):
    client = _get_supabase_client()
    _get_user_id(authorization)
    result = (
        client.table("node_comments")
        .select("*")
        .eq("flow_id", flow_id)
        .order("created_at")
        .execute()
    )
    return {"comments": result.data}


@router.patch("/flows/{flow_id}/comments/{comment_id}", summary="Resolve a comment")
async def resolve_comment(
    flow_id: str,
    comment_id: str,
    authorization: str | None = Header(None),
):
    client = _get_supabase_client()
    _get_user_id(authorization)
    client.table("node_comments").update({"resolved": True}).eq("id", comment_id).execute()
    return {"resolved": True}
