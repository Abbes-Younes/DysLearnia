"""
blocks/transform/key_concepts.py — Key concepts extraction block.
"""
from __future__ import annotations

from blocks.base import BlockData, BlockDescription, IBlock
from blocks.registry import register_block
from mixins.rag_mixin import RAGMixin


@register_block
class KeyConceptsBlock(IBlock, RAGMixin):
    description = BlockDescription(
        name="key_concepts",
        display_name="Key Concepts",
        group="transform",
        input_types=["text"],
        output_types=["text"],
        parameters=[
            {
                "name": "max_concepts",
                "type": "slider",
                "min": 5,
                "max": 30,
                "default": 10,
                "label": "Maximum concepts to extract",
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
You are an expert at identifying the most important concepts in educational text.

Extract exactly {max_concepts} key concepts from the text below.
For each concept output:
  - **Concept name** (bold): One clear definition sentence.
Reading level: {level}

Rules:
- Order from most to least important.
- Use simple language appropriate for the reading level.
- No introductory sentences. Output the list only.
""".strip()

    async def execute(self, inputs: list[BlockData], params: dict) -> list[BlockData]:
        from langchain_core.prompts import ChatPromptTemplate
        from models.local_llm import get_llm

        text = self.first_text(inputs)
        if not text:
            return [BlockData(text="", metadata={"error": "No text input"})]

        max_c = int(params.get("max_concepts", 10))
        level = params.get("reading_level", "adult")

        doc_id = inputs[0].metadata.get("doc_id", "") if inputs else ""
        chunks = self._retrieve(text[:200], doc_id) if doc_id else []

        system = self._SYSTEM_PROMPT.format(max_concepts=max_c, level=level)
        if chunks:
            system = self._grounded_prompt(system, chunks)

        prompt = ChatPromptTemplate.from_messages([
            ("system", system),
            ("human", "Text:\n{text}"),
        ])
        chain = prompt | get_llm()
        result = chain.invoke({"text": text})
        output = result.content.strip()

        return [BlockData(
            text=output,
            mime_type="text/plain",
            metadata={
                "confidence": self._confidence_score(output),
                "concept_count": max_c,
            },
            source_chunks=chunks,
        )]
