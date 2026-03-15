"""
blocks/transform/quiz_builder.py — Quiz builder block.

Wraps the existing quiz agent with the IBlock interface.
"""
from __future__ import annotations

import json

from blocks.base import BlockData, BlockDescription, IBlock
from blocks.registry import register_block
from mixins.rag_mixin import RAGMixin


@register_block
class QuizBuilderBlock(IBlock, RAGMixin):
    description = BlockDescription(
        name="quiz_builder",
        display_name="Quiz Builder",
        group="transform",
        input_types=["text"],
        output_types=["text"],
        parameters=[
            {
                "name": "count",
                "type": "slider",
                "min": 3,
                "max": 15,
                "default": 5,
                "label": "Number of questions",
            },
            {
                "name": "types",
                "type": "select",
                "options": ["MCQ", "true_false", "short_answer"],
                "default": "MCQ",
                "label": "Question type",
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
        from agents.quiz import quiz_node
        from models.local_llm import get_llm

        text = self.first_text(inputs)
        if not text:
            return [BlockData(text="[]", metadata={"error": "No text input"})]

        doc_id = inputs[0].metadata.get("doc_id", "") if inputs else ""
        chunks = self._retrieve(text[:200], doc_id) if doc_id else []

        state = {
            "text": text,
            "reading_level": params.get("reading_level", "adult"),
        }
        llm = get_llm()
        result = quiz_node(state, llm)

        questions = result.get("quiz", [])
        # Serialise to JSON text so downstream blocks can consume it
        try:
            quiz_json = json.dumps(
                [q.model_dump() if hasattr(q, "model_dump") else q for q in questions],
                ensure_ascii=False,
                indent=2,
            )
        except Exception:
            quiz_json = str(questions)

        return [BlockData(
            text=quiz_json,
            mime_type="application/json",
            metadata={
                "question_count": len(questions),
                "quiz_type": params.get("types", "MCQ"),
            },
            source_chunks=chunks,
        )]
