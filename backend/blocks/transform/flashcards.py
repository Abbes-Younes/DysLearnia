"""
blocks/transform/flashcards.py — Flashcard generation block.
"""
from __future__ import annotations

import json

from blocks.base import BlockData, BlockDescription, IBlock
from blocks.registry import register_block
from mixins.rag_mixin import RAGMixin


@register_block
class FlashcardsBlock(IBlock, RAGMixin):
    description = BlockDescription(
        name="flashcards",
        display_name="Flashcard Generator",
        group="transform",
        input_types=["text"],
        output_types=["text"],
        parameters=[
            {
                "name": "count",
                "type": "slider",
                "min": 5,
                "max": 50,
                "default": 10,
                "label": "Number of flashcards",
            },
            {
                "name": "difficulty",
                "type": "select",
                "options": ["easy", "medium", "hard"],
                "default": "medium",
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
You are a flashcard creator for dyslexic learners.

Generate exactly {count} flashcards from the course text below.
Return a JSON array of objects, each with:
  "front": the question or term (max 15 words)
  "back":  the answer or definition (max 30 words)

Difficulty: {difficulty}. Reading level: {level}.
Rules:
- Return ONLY the JSON array, no markdown fences.
- Questions should test understanding, not just recall.
""".strip()

    async def execute(self, inputs: list[BlockData], params: dict) -> list[BlockData]:
        from langchain_core.prompts import ChatPromptTemplate
        from models.local_llm import get_llm

        text = self.first_text(inputs)
        if not text:
            return [BlockData(text="[]", metadata={"error": "No text input"})]

        count = int(params.get("count", 10))
        difficulty = params.get("difficulty", "medium")
        level = params.get("reading_level", "adult")

        doc_id = inputs[0].metadata.get("doc_id", "") if inputs else ""
        chunks = self._retrieve(text[:200], doc_id) if doc_id else []

        system = self._SYSTEM_PROMPT.format(count=count, difficulty=difficulty, level=level)
        if chunks:
            system = self._grounded_prompt(system, chunks)

        prompt = ChatPromptTemplate.from_messages([
            ("system", system),
            ("human", "Text:\n{text}"),
        ])
        chain = prompt | get_llm()
        result = chain.invoke({"text": text})
        raw = result.content.strip()

        # Try to parse JSON; fall back to raw text
        try:
            cards = json.loads(raw)
            output = json.dumps(cards, ensure_ascii=False, indent=2)
        except json.JSONDecodeError:
            output = raw

        return [BlockData(
            text=output,
            mime_type="application/json",
            metadata={
                "card_count": count,
                "difficulty": difficulty,
            },
            source_chunks=chunks,
        )]
