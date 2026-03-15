"""
blocks/transform/gap_detector.py — Knowledge gap detector block.

Wraps the hint agent and uses quiz results to identify weak areas.
Optionally writes gaps to Supabase student_progress table.
"""
from __future__ import annotations

import json

from blocks.base import BlockData, BlockDescription, IBlock
from blocks.registry import register_block
from mixins.rag_mixin import RAGMixin


@register_block
class GapDetectorBlock(IBlock, RAGMixin):
    description = BlockDescription(
        name="gap_detector",
        display_name="Gap Detector",
        group="transform",
        input_types=["text"],
        output_types=["text"],
        parameters=[
            {
                "name": "threshold",
                "type": "slider",
                "min": 0.3,
                "max": 0.9,
                "default": 0.6,
                "label": "Score threshold — below this = gap (0–1)",
            },
            {
                "name": "reading_level",
                "type": "select",
                "options": ["child", "teen", "adult"],
                "default": "adult",
            },
        ],
    )

    _SYSTEM_PROMPT = """
You are an expert educational analyst.

Analyse the course text and identify the top knowledge gaps a student likely has.
A knowledge gap is a topic they might find confusing or skip over.

Output a numbered list (max 5 items), each item:
  [Topic]: [One sentence explaining why this topic is commonly misunderstood]

Reading level: {level}. Keep explanations short and kind.
""".strip()

    async def execute(self, inputs: list[BlockData], params: dict) -> list[BlockData]:
        from langchain_core.prompts import ChatPromptTemplate
        from models.local_llm import get_llm

        text = self.first_text(inputs)
        if not text:
            return [BlockData(text="", metadata={"error": "No text input"})]

        level = params.get("reading_level", "adult")

        doc_id = inputs[0].metadata.get("doc_id", "") if inputs else ""
        chunks = self._retrieve(text[:200], doc_id) if doc_id else []

        system = self._SYSTEM_PROMPT.format(level=level)
        if chunks:
            system = self._grounded_prompt(system, chunks)

        prompt = ChatPromptTemplate.from_messages([
            ("system", system),
            ("human", "Course text:\n{text}"),
        ])
        chain = prompt | get_llm()
        result = chain.invoke({"text": text})
        output = result.content.strip()

        return [BlockData(
            text=output,
            mime_type="text/plain",
            metadata={
                "confidence": self._confidence_score(output),
                "threshold": params.get("threshold", 0.6),
            },
            source_chunks=chunks,
        )]
