"""
mixins/rag_mixin.py — RAG retrieval mixin for LLM blocks.

Every LLM block inherits RAGMixin to ground its output in source document
chunks from Qdrant Cloud. Low confidence scores surface as UI warning badges.
"""
from __future__ import annotations

import re


class RAGMixin:
    """
    Mixin that adds Qdrant Cloud RAG retrieval and confidence scoring.

    Usage:
        class MyBlock(IBlock, RAGMixin):
            async def execute(self, inputs, params):
                doc_id = inputs[0].metadata.get("doc_id", "")
                chunks = self._retrieve("my query", doc_id)
                prompt = self._grounded_prompt("summarise", chunks)
                ...
    """

    def _retrieve(self, query: str, doc_id: str, k: int = 5) -> list[str]:
        """Embed query, retrieve top-k chunks from Qdrant Cloud."""
        from db.qdrant import retrieve
        if not doc_id:
            return []
        return retrieve(doc_id, query, k)

    def _grounded_prompt(self, task: str, chunks: list[str]) -> str:
        """
        Wrap a task instruction in a strict grounding envelope.
        Forces the LLM to use only the provided excerpts.
        """
        if not chunks:
            return task
        excerpts = "\n\n---\n\n".join(chunks)
        return (
            f"Use ONLY the following excerpts to complete the task below. "
            f"If you cannot complete the task from the excerpts alone, "
            f"say exactly [INSUFFICIENT CONTEXT].\n\n"
            f"EXCERPTS:\n{excerpts}\n\n"
            f"TASK: {task}"
        )

    # Ungrounded hedge patterns — each match lowers confidence
    _HEDGE_PATTERNS = re.compile(
        r"\b(generally|typically|usually|often|I think|I believe|might|may|could be|"
        r"probably|perhaps|possibly|in general|it seems|it appears|as far as I know|"
        r"to my knowledge|approximately|roughly|more or less)\b",
        re.IGNORECASE,
    )

    def _confidence_score(self, output: str) -> float:
        """
        Detect ungrounded hedges in LLM output.
        Returns 0.0–1.0. Low score = yellow warning badge in UI.
        """
        if not output:
            return 0.0
        hedges = self._HEDGE_PATTERNS.findall(output)
        # Each hedge reduces confidence by 0.1, floor at 0.0
        score = max(0.0, 1.0 - len(hedges) * 0.1)
        return round(score, 2)
