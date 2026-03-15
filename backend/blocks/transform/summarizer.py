"""
blocks/transform/summarizer.py — Summarizer block.

Wraps the existing simplifier agent, adding IBlock interface and RAGMixin.
"""
from __future__ import annotations

from blocks.base import BlockData, BlockDescription, IBlock
from blocks.registry import register_block
from mixins.rag_mixin import RAGMixin


@register_block
class SummarizerBlock(IBlock, RAGMixin):
    description = BlockDescription(
        name="summarizer",
        display_name="Summarizer",
        group="transform",
        input_types=["text"],
        output_types=["text"],
        parameters=[
            {
                "name": "ratio",
                "type": "slider",
                "min": 0.1,
                "max": 0.9,
                "default": 0.4,
                "label": "Compression ratio (0.1 = very short, 0.9 = near-full)",
            },
            {
                "name": "style",
                "type": "select",
                "options": ["bullets", "paragraph", "tldr"],
                "default": "paragraph",
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
        from langchain_core.prompts import ChatPromptTemplate
        from models.local_llm import get_llm

        text = self.first_text(inputs)
        if not text:
            return [BlockData(text="", metadata={"error": "No text input"})]

        level = params.get("reading_level", "adult")
        style = params.get("style", "paragraph")
        ratio = params.get("ratio", 0.4)

        # RAG grounding: retrieve relevant chunks if doc_id available
        doc_id = inputs[0].metadata.get("doc_id", "") if inputs else ""
        chunks = self._retrieve(text[:200], doc_id) if doc_id else []
        source_chunks = chunks

        STYLE_HINT = {
            "bullets": "Format the summary as bullet points (3–7 bullets).",
            "paragraph": "Format the summary as one to three flowing paragraphs.",
            "tldr": "Start with 'TL;DR:' and write one sentence only.",
        }

        prompt_text = (
            f"Summarise the following course text at the {level!r} reading level "
            f"to approximately {int(ratio * 100)}% of its original length.\n"
            f"{STYLE_HINT.get(style, '')}\n"
            "Keep all key ideas. Use simple, active-voice sentences."
        )
        if chunks:
            prompt_text = self._grounded_prompt(prompt_text, chunks)

        prompt = ChatPromptTemplate.from_messages([
            ("system", prompt_text),
            ("human", "Text to summarise:\n{text}"),
        ])
        chain = prompt | get_llm()
        result = chain.invoke({"text": text})
        output_text = result.content.strip()

        confidence = self._confidence_score(output_text)
        return [BlockData(
            text=output_text,
            mime_type="text/plain",
            metadata={
                "confidence": confidence,
                "word_count": len(output_text.split()),
                "reading_level": level,
            },
            source_chunks=source_chunks,
        )]
