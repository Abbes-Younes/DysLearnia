"""
blocks/transform/knowledge_graph.py — Knowledge graph block.

Uses the LLM to extract concept triples from text, writes them to Neo4j,
and returns a D3-compatible JSON graph + plain text summary.
"""
from __future__ import annotations

import json
import re

from blocks.base import BlockData, BlockDescription, IBlock
from blocks.registry import register_block
from mixins.rag_mixin import RAGMixin


@register_block
class KnowledgeGraphBlock(IBlock, RAGMixin):
    description = BlockDescription(
        name="knowledge_graph",
        display_name="Knowledge Graph",
        group="transform",
        input_types=["text"],
        output_types=["text"],
        parameters=[
            {
                "name": "depth",
                "type": "slider",
                "min": 1,
                "max": 3,
                "default": 2,
                "label": "Graph depth (1=concepts only, 3=deep relations)",
            },
            {
                "name": "min_confidence",
                "type": "slider",
                "min": 0.1,
                "max": 1.0,
                "default": 0.5,
                "label": "Minimum relation confidence",
            },
        ],
    )

    _SYSTEM_PROMPT = """
You are a knowledge graph extractor.

Extract concept relationships from the text below.
Return a JSON array of triples:
  [["SubjectConcept", "RELATION_TYPE", "ObjectConcept"], ...]

Rules:
- RELATION_TYPE should be uppercase with underscores (e.g. IS_A, CAUSES, REQUIRES, PART_OF).
- Extract 10–20 triples.
- Both concepts must appear in the text.
- Return ONLY the JSON array — no markdown fences, no explanation.
""".strip()

    async def execute(self, inputs: list[BlockData], params: dict) -> list[BlockData]:
        from langchain_core.prompts import ChatPromptTemplate
        from models.local_llm import get_llm

        text = self.first_text(inputs)
        if not text:
            return [BlockData(text="{}", mime_type="application/json",
                              metadata={"error": "No text input"})]

        doc_id = inputs[0].metadata.get("doc_id", "") if inputs else ""
        user_id = inputs[0].metadata.get("user_id", "") if inputs else ""

        prompt = ChatPromptTemplate.from_messages([
            ("system", self._SYSTEM_PROMPT),
            ("human", "Text:\n{text}"),
        ])
        chain = prompt | get_llm()
        result = chain.invoke({"text": text})
        raw = result.content.strip()

        # Parse triples
        triples: list[tuple[str, str, str]] = []
        try:
            parsed = json.loads(raw)
            for item in parsed:
                if isinstance(item, list) and len(item) == 3:
                    triples.append((str(item[0]), str(item[1]), str(item[2])))
        except json.JSONDecodeError:
            # Fallback: regex extraction
            for m in re.finditer(r'\["([^"]+)"\s*,\s*"([^"]+)"\s*,\s*"([^"]+)"\]', raw):
                triples.append((m.group(1), m.group(2), m.group(3)))

        # Write to Neo4j (async, best-effort)
        if doc_id and triples:
            try:
                from db.neo4j import upsert_graph
                await upsert_graph(doc_id, triples)
            except Exception:
                pass  # Neo4j unavailable — still return the graph JSON

        # Build D3 graph structure
        node_names = {}
        for subj, _, obj in triples:
            node_names[subj] = node_names.get(subj, len(node_names))
            node_names[obj] = node_names.get(obj, len(node_names))

        d3_nodes = [{"id": idx, "name": name} for name, idx in node_names.items()]
        d3_links = [
            {
                "source": node_names[s],
                "target": node_names[o],
                "label": r,
            }
            for s, r, o in triples
        ]
        graph = {"nodes": d3_nodes, "links": d3_links}
        graph_json = json.dumps(graph, ensure_ascii=False, indent=2)

        return [BlockData(
            text=graph_json,
            mime_type="application/json",
            metadata={
                "graph_nodes": len(d3_nodes),
                "graph_links": len(d3_links),
                "doc_id": doc_id,
            },
        )]
