"""
tests/test_neo4j_integration.py — Integration tests for Neo4j db layer.

Requires a running Neo4j instance at bolt://localhost:7687 with
credentials neo4j/dyslearnia.
Skip automatically if Neo4j is not reachable.
"""
import os
import uuid

import pytest

# Point at local container
os.environ.setdefault("NEO4J_URI", "bolt://localhost:7687")
os.environ.setdefault("NEO4J_USER", "neo4j")
os.environ.setdefault("NEO4J_PASSWORD", "dyslearnia")


def _neo4j_available() -> bool:
    try:
        import httpx
        r = httpx.get("http://localhost:7474", timeout=5)
        return r.status_code == 200
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _neo4j_available(),
    reason="Neo4j not reachable at localhost:7474",
)


@pytest.fixture(autouse=True)
def reset_neo4j_driver():
    """Reset cached driver so env vars are picked up fresh."""
    import db.neo4j as n
    if n._driver:
        try:
            import asyncio
            asyncio.get_event_loop().run_until_complete(n._driver.close())
        except Exception:
            pass
    n._driver = None
    yield
    if n._driver:
        try:
            import asyncio
            asyncio.get_event_loop().run_until_complete(n._driver.close())
        except Exception:
            pass
    n._driver = None


# ── upsert_graph ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_upsert_graph_returns_true():
    from db.neo4j import upsert_graph
    doc_id = f"test-{uuid.uuid4()}"
    triples = [("Mitochondria", "IS_PART_OF", "Cell")]
    result = await upsert_graph(doc_id, triples)
    assert result is True


@pytest.mark.asyncio
async def test_upsert_graph_multiple_triples():
    from db.neo4j import upsert_graph
    doc_id = f"test-{uuid.uuid4()}"
    triples = [
        ("Photosynthesis", "REQUIRES", "Sunlight"),
        ("Photosynthesis", "REQUIRES", "Water"),
        ("Photosynthesis", "PRODUCES", "Glucose"),
        ("Photosynthesis", "PRODUCES", "Oxygen"),
    ]
    result = await upsert_graph(doc_id, triples)
    assert result is True


@pytest.mark.asyncio
async def test_upsert_graph_idempotent():
    """Re-upserting the same triples should not raise or duplicate nodes."""
    from db.neo4j import upsert_graph
    doc_id = f"test-{uuid.uuid4()}"
    triples = [("DNA", "ENCODES", "Protein")]
    await upsert_graph(doc_id, triples)
    result = await upsert_graph(doc_id, triples)  # second upsert
    assert result is True


# ── get_neighborhood ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_neighborhood_returns_d3_structure():
    from db.neo4j import upsert_graph, get_neighborhood
    doc_id = f"test-{uuid.uuid4()}"
    triples = [
        ("Osmosis", "IS_TYPE_OF", "Diffusion"),
        ("Diffusion", "REQUIRES", "Concentration_Gradient"),
    ]
    await upsert_graph(doc_id, triples)

    result = await get_neighborhood("Osmosis", doc_id, depth=2)
    assert "nodes" in result
    assert "links" in result
    assert isinstance(result["nodes"], list)
    assert isinstance(result["links"], list)


@pytest.mark.asyncio
async def test_get_neighborhood_has_correct_concept():
    from db.neo4j import upsert_graph, get_neighborhood
    doc_id = f"test-{uuid.uuid4()}"
    triples = [("Enzyme", "CATALYSES", "Reaction")]
    await upsert_graph(doc_id, triples)

    result = await get_neighborhood("Enzyme", doc_id, depth=1)
    node_names = [n["name"] for n in result["nodes"]]
    assert any("Enzyme" in name for name in node_names)


@pytest.mark.asyncio
async def test_get_neighborhood_unknown_concept_returns_empty():
    from db.neo4j import get_neighborhood
    result = await get_neighborhood("NonExistentConcept_XYZ", "nonexistent-doc", depth=1)
    assert result["nodes"] == []
    assert result["links"] == []


# ── KnowledgeGraphBlock integration ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_knowledge_graph_block_writes_to_neo4j():
    """
    KnowledgeGraphBlock with mocked LLM should write triples to Neo4j
    and return a valid D3 JSON structure.
    """
    from unittest.mock import MagicMock, patch
    from blocks.base import BlockData
    from blocks.transform.knowledge_graph import KnowledgeGraphBlock

    doc_id = f"kg-test-{uuid.uuid4()}"
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = (
        '[["Nucleus", "CONTAINS", "DNA"], '
        '["DNA", "ENCODES", "RNA"], '
        '["RNA", "PRODUCES", "Protein"]]'
    )
    mock_llm.return_value = mock_response

    block = KnowledgeGraphBlock()
    inputs = [BlockData(
        text="The nucleus contains DNA which encodes RNA which produces protein.",
        metadata={"doc_id": doc_id},
    )]

    with patch("models.local_llm.get_llm", return_value=mock_llm):
        results = await block.execute(inputs, {"depth": 2})

    assert len(results) == 1
    bd = results[0]
    assert bd.mime_type == "application/json"
    import json
    graph = json.loads(bd.text)
    assert "nodes" in graph
    assert "links" in graph
    assert len(graph["nodes"]) >= 3
    assert bd.metadata["doc_id"] == doc_id
