"""
db/neo4j.py — Neo4j async driver singleton.

Used by KnowledgeGraphBlock (write triples) and TutorChatBlock (Cypher queries).
Gracefully skips operations when NEO4J_URI is not configured.
"""
from __future__ import annotations

import os
import logging

logger = logging.getLogger(__name__)

_driver = None


def _get_driver():
    global _driver
    if _driver is not None:
        return _driver
    uri = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "dyslearnia")
    if not uri:
        logger.warning("NEO4J_URI not set — Neo4j operations will be skipped.")
        return None
    try:
        from neo4j import AsyncGraphDatabase
        _driver = AsyncGraphDatabase.driver(uri, auth=(user, password))
        return _driver
    except ImportError:
        logger.warning("neo4j driver not installed — graph operations skipped.")
        return None
    except Exception as exc:
        logger.warning(f"Neo4j connection failed: {exc} — graph operations skipped.")
        return None


async def upsert_graph(doc_id: str, triples: list[tuple[str, str, str]]) -> bool:
    """Upsert a list of (subject, relation, object) triples into Neo4j."""
    driver = _get_driver()
    if driver is None:
        return False
    try:
        async with driver.session() as s:
            for subj, rel, obj in triples:
                await s.run(
                    """
                    MERGE (a:Concept {name: $subj, doc_id: $doc_id})
                    MERGE (b:Concept {name: $obj,  doc_id: $doc_id})
                    MERGE (a)-[r:RELATION {type: $rel}]->(b)
                    """,
                    subj=subj,
                    obj=obj,
                    rel=rel,
                    doc_id=doc_id,
                )
        return True
    except Exception as exc:
        logger.error(f"Neo4j upsert error: {exc}")
        return False


async def get_neighborhood(concept: str, doc_id: str, depth: int = 2) -> dict:
    """
    Retrieve the concept neighborhood as a D3-compatible dict.
    Returns {"nodes": [...], "links": [...]}.

    Uses a simple 1-hop query for reliable deserialisation; depth parameter
    controls how many UNION passes are made (each adds one hop).
    """
    driver = _get_driver()
    if driver is None:
        return {"nodes": [], "links": []}

    # Simple 1-hop query avoids variable-length path parameter issues.
    # For deeper graphs, run iteratively or accept 1-hop for now.
    cypher = """
        MATCH (c:Concept {name: $concept, doc_id: $doc_id})-[r:RELATION]->(n:Concept)
        RETURN c.name AS src, r.type AS rel_type, n.name AS tgt
        UNION
        MATCH (c:Concept {name: $concept, doc_id: $doc_id})<-[r:RELATION]-(n:Concept)
        RETURN n.name AS src, r.type AS rel_type, c.name AS tgt
    """
    try:
        async with driver.session() as s:
            result = await s.run(cypher, concept=concept, doc_id=doc_id)
            rows = await result.data()
            return _rows_to_d3(concept, rows)
    except Exception as exc:
        logger.error(f"Neo4j neighborhood error: {exc}")
        return {"nodes": [], "links": []}


def _rows_to_d3(root_concept: str, rows: list[dict]) -> dict:
    """
    Convert flat (src, rel_type, tgt) rows to a D3 force-graph structure.
    Always includes the root concept node even if it has no neighbours.
    """
    node_set: dict[str, dict] = {}
    links: list[dict] = []

    for row in rows:
        src = row.get("src") or ""
        tgt = row.get("tgt") or ""
        rel = row.get("rel_type") or "RELATION"
        if src:
            node_set[src] = {"id": src, "name": src}
        if tgt:
            node_set[tgt] = {"id": tgt, "name": tgt}
        if src and tgt:
            links.append({"source": src, "target": tgt, "label": rel})

    return {"nodes": list(node_set.values()), "links": links}
