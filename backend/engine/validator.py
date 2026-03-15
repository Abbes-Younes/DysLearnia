"""
engine/validator.py — Edge type-compatibility validation.

Enforces that blocks are only connected when their output/input types match.
The frontend calls GET /api/blocks and uses input_types/output_types to draw
red snaps; this module does the same check server-side before every run.
"""
from __future__ import annotations

# Which output types are accepted by which block keys
COMPATIBILITY: dict[str, list[str]] = {
    "text": [
        "summarizer",
        "key_concepts",
        "knowledge_graph",
        "flashcards",
        "quiz_builder",
        "simplified_text",
        "dyslexia_font",
        "tts",
        "infographic",
        "pdf_unifier",
        "pptx_unifier",
        "audio_unifier",
        "gap_detector",
        "gamification",
        "tutor_chat",
    ],
    "binary/png": ["pdf_unifier", "pptx_unifier", "video_unifier"],
    "binary/wav": ["video_unifier", "audio_unifier"],
    "binary/pdf": ["course_input"],
    "graph": ["tutor_chat"],
    "binary/*": [],   # player/preview only — no downstream processing blocks
}


def validate_edge(output_type: str, target_block_name: str) -> bool:
    """
    Return True if a block that outputs `output_type` may connect to
    a block named `target_block_name`.
    """
    # Wildcard match (e.g. "binary/*" accepts any target that accepts binary)
    if output_type.endswith("/*"):
        base = output_type[:-2]
        for key, targets in COMPATIBILITY.items():
            if key.startswith(base) and target_block_name in targets:
                return True
        return False
    return target_block_name in COMPATIBILITY.get(output_type, [])


def validate_pipeline(nodes: list[dict], edges: list[dict]) -> list[str]:
    """
    Validate all edges in a pipeline definition.

    Returns a list of human-readable error strings (empty = valid).
    """
    from blocks.registry import BLOCK_REGISTRY

    errors: list[str] = []
    node_map = {n["id"]: n for n in nodes}

    for edge in edges:
        src_id = edge.get("source")
        tgt_id = edge.get("target")

        if src_id not in node_map:
            errors.append(f"Edge references unknown source node: {src_id!r}")
            continue
        if tgt_id not in node_map:
            errors.append(f"Edge references unknown target node: {tgt_id!r}")
            continue

        # Node type is stored under "type" or "data.block_type"
        src_node = node_map[src_id]
        tgt_node = node_map[tgt_id]
        src_type = src_node.get("type") or src_node.get("data", {}).get("block_type")
        tgt_type = tgt_node.get("type") or tgt_node.get("data", {}).get("block_type")

        if src_type not in BLOCK_REGISTRY:
            errors.append(f"Unknown block type on source node {src_id!r}: {src_type!r}")
            continue
        if tgt_type not in BLOCK_REGISTRY:
            errors.append(f"Unknown block type on target node {tgt_id!r}: {tgt_type!r}")
            continue

        src_block_cls = BLOCK_REGISTRY[src_type]
        for out_type in src_block_cls.description.output_types:
            if not validate_edge(out_type, tgt_type):
                errors.append(
                    f"Incompatible edge: {src_type} (outputs {out_type!r}) "
                    f"→ {tgt_type} (does not accept {out_type!r})"
                )

    return errors
