"""
blocks/base.py — Core IBlock abstractions.

BlockData is the universal envelope passed between every block.
IBlock is the interface every processing node must implement.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class BlockData:
    """Universal data envelope passed between blocks in a pipeline."""

    text: str | None = None
    binary: bytes | None = None
    mime_type: str | None = None  # "audio/wav" | "text/html" | "image/png" | "application/pdf"
    metadata: dict[str, Any] = field(default_factory=dict)
    # metadata keys (non-exhaustive):
    #   confidence: float       — hallucination score 0.0–1.0
    #   word_count: int
    #   reading_level: str      — A1/A2/B1/B2/C1/C2
    #   graph_nodes: int        — for knowledge graph blocks
    #   audio_duration_s: float
    #   filename: str           — for download blocks
    source_chunks: list[str] = field(default_factory=list)
    # the RAG excerpts that grounded this output — shown as citations in UI


@dataclass
class BlockDescription:
    """Static metadata for a block — drives the frontend palette and validator."""

    name: str           # machine key: "summarizer"
    display_name: str   # UI label: "Summarizer"
    group: str          # "input" | "transform" | "output" | "intelligence"
    input_types: list[str]   # ["text"] | ["binary/audio"] | ["text", "binary/pdf"]
    output_types: list[str]  # ["text"] | ["binary/audio"] | ["graph"]
    parameters: list[dict]   # schema rendered by frontend into sliders/selects


class IBlock(ABC):
    """Every processing node in the pipeline implements this interface."""

    description: BlockDescription

    @abstractmethod
    async def execute(
        self,
        inputs: list[BlockData],
        params: dict[str, Any],
    ) -> list[BlockData]:
        """
        Execute the block.

        Args:
            inputs: Outputs of all upstream connected nodes.
            params: User-configured parameters for this block instance.

        Returns:
            A list of BlockData outputs (usually one item).
        """
        ...

    def first_text(self, inputs: list[BlockData]) -> str:
        """Helper: return the first text payload from inputs, or empty string."""
        for bd in inputs:
            if bd.text:
                return bd.text
        return ""
