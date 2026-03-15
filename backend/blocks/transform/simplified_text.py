"""
blocks/transform/simplified_text.py — Simplified text block.

Rewrites text for dyslexic learners at a specified reading level (A1–C2 CEFR).
Wraps the existing simplifier agent with the IBlock interface.
"""
from __future__ import annotations

from blocks.base import BlockData, BlockDescription, IBlock
from blocks.registry import register_block
from mixins.rag_mixin import RAGMixin


@register_block
class SimplifiedTextBlock(IBlock, RAGMixin):
    description = BlockDescription(
        name="simplified_text",
        display_name="Simplified Text",
        group="transform",
        input_types=["text"],
        output_types=["text"],
        parameters=[
            {
                "name": "level",
                "type": "select",
                "options": ["A1", "A2", "B1", "B2", "C1", "C2"],
                "default": "B1",
                "label": "CEFR level (A1=simplest, C2=native)",
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
        from agents.simplifier import simplifier_node
        from models.local_llm import get_llm

        text = self.first_text(inputs)
        if not text:
            return [BlockData(text="", metadata={"error": "No text input"})]

        reading_level = params.get("reading_level", "adult")
        # Map CEFR level to reading_level if provided
        cefr = params.get("level", "B1")
        cefr_to_rl = {
            "A1": "child", "A2": "child",
            "B1": "teen", "B2": "teen",
            "C1": "adult", "C2": "adult",
        }
        effective_level = cefr_to_rl.get(cefr, reading_level)

        state = {
            "text": text,
            "reading_level": effective_level,
        }
        llm = get_llm()
        result = simplifier_node(state, llm)

        output = result.get("simplified_text") or result.get("simplified_text_error", "")
        confidence = self._confidence_score(output)

        return [BlockData(
            text=output,
            mime_type="text/plain",
            metadata={
                "confidence": confidence,
                "cefr_level": cefr,
                "reading_level": effective_level,
                "word_count": len(output.split()),
            },
        )]
