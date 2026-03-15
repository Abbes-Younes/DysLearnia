"""
blocks/transform/gamification.py — Gamification block.

Wraps the existing gamification agent with the IBlock interface.
"""
from __future__ import annotations

import json

from blocks.base import BlockData, BlockDescription, IBlock
from blocks.registry import register_block


@register_block
class GamificationBlock(IBlock):
    description = BlockDescription(
        name="gamification",
        display_name="Gamification",
        group="transform",
        input_types=["text"],
        output_types=["text"],
        parameters=[
            {
                "name": "xp_multiplier",
                "type": "slider",
                "min": 1,
                "max": 5,
                "default": 1,
                "label": "XP multiplier (streak bonus)",
            },
            {
                "name": "reading_level",
                "type": "select",
                "options": ["child", "teen", "adult"],
                "default": "adult",
            },
        ],
    )

    async def execute(self, inputs: list[BlockData], params: dict) -> list[BlockData]:
        from agents.gamification import gamification_node
        from models.local_llm import get_llm

        # Accept progress from metadata or build from params
        progress = None
        for bd in inputs:
            if bd.metadata.get("quiz_results"):
                progress = bd.metadata["quiz_results"]
                break

        if progress is None:
            progress = {
                "score": params.get("score", 0),
                "total": params.get("total", 0),
                "streak": params.get("streak", 1),
                "age_group": params.get("reading_level", "adult"),
            }

        state = {
            "progress": progress,
            "reading_level": params.get("reading_level", "adult"),
        }
        llm = get_llm()
        result = gamification_node(state, llm)
        gamification = result.get("gamification")

        if gamification:
            try:
                out = gamification.model_dump()
            except AttributeError:
                out = vars(gamification)
            text = json.dumps(out, ensure_ascii=False, indent=2)
        else:
            text = json.dumps({"error": result.get("gamification_error", "Unknown error")})

        return [BlockData(text=text, mime_type="application/json")]
