"""
db/qdrant.py — Qdrant Cloud client singleton.

All embeddings live in Qdrant Cloud (free tier).
The single `course_chunks` collection handles per-doc RAG and cross-doc search.

Functions gracefully no-op when QDRANT_URL is not set (dev / CI mode).
"""
from __future__ import annotations

import os
import logging

logger = logging.getLogger(__name__)

_client = None
_embedder = None
COLLECTION = "course_chunks"


def _get_client():
    global _client
    if _client is not None:
        return _client
    url = os.getenv("QDRANT_URL")
    api_key = os.getenv("QDRANT_API_KEY")
    if not url:
        logger.warning("QDRANT_URL not set — Qdrant operations will be skipped.")
        return None
    try:
        from qdrant_client import QdrantClient
        _client = QdrantClient(url=url, api_key=api_key)
        return _client
    except ImportError:
        logger.warning("qdrant-client not installed — Qdrant operations will be skipped.")
        return None


def _get_embedder():
    global _embedder
    if _embedder is not None:
        return _embedder
    try:
        from sentence_transformers import SentenceTransformer
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
        return _embedder
    except ImportError:
        logger.warning("sentence-transformers not installed — embeddings unavailable.")
        return None


def ensure_collection():
    client = _get_client()
    if client is None:
        return
    from qdrant_client.models import VectorParams, Distance
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION not in existing:
        client.create_collection(
            COLLECTION,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )


def index_document(doc_id: str, user_id: str, chunks: list[str]) -> bool:
    """Chunk a document and upsert all vectors into Qdrant Cloud."""
    client = _get_client()
    embedder = _get_embedder()
    if client is None or embedder is None:
        return False
    ensure_collection()
    from qdrant_client.models import PointStruct
    points = [
        PointStruct(
            id=abs(hash(f"{doc_id}:{i}")) % (2 ** 63),
            vector=embedder.encode(chunk).tolist(),
            payload={
                "doc_id": doc_id,
                "user_id": user_id,
                "text": chunk,
                "chunk_index": i,
            },
        )
        for i, chunk in enumerate(chunks)
    ]
    client.upsert(COLLECTION, points=points)
    return True


def retrieve(doc_id: str, query: str, k: int = 5) -> list[str]:
    """Per-document RAG — retrieve top-k chunks filtered by doc_id."""
    client = _get_client()
    embedder = _get_embedder()
    if client is None or embedder is None:
        return []
    from qdrant_client.models import Filter, FieldCondition, MatchValue
    results = client.query_points(
        COLLECTION,
        query=embedder.encode(query).tolist(),
        limit=k,
        query_filter=Filter(
            must=[FieldCondition(key="doc_id", match=MatchValue(value=doc_id))]
        ),
    ).points
    return [r.payload["text"] for r in results]


def get_all_chunks(doc_id: str) -> list[str]:
    """
    Return ALL stored chunks for a doc_id in original paragraph order.
    Uses scroll (full scan) rather than query_points so no chunks are dropped.
    Returns [] when Qdrant is unavailable.
    """
    client = _get_client()
    if client is None:
        return []
    from qdrant_client.models import Filter, FieldCondition, MatchValue, OrderBy
    doc_filter = Filter(must=[FieldCondition(key="doc_id", match=MatchValue(value=doc_id))])
    records: list = []
    offset = None
    while True:
        batch, offset = client.scroll(
            COLLECTION,
            scroll_filter=doc_filter,
            limit=100,
            offset=offset,
            with_payload=True,
            order_by=OrderBy(key="chunk_index", direction="asc"),
        )
        records.extend(batch)
        if offset is None:
            break
    return [r.payload["text"] for r in records]


def search_all_docs(user_id: str, query: str, k: int = 10) -> list[dict]:
    """Cross-document search filtered by user_id."""
    client = _get_client()
    embedder = _get_embedder()
    if client is None or embedder is None:
        return []
    from qdrant_client.models import Filter, FieldCondition, MatchValue
    results = client.query_points(
        COLLECTION,
        query=embedder.encode(query).tolist(),
        limit=k,
        query_filter=Filter(
            must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]
        ),
    ).points
    return [
        {"text": r.payload["text"], "doc_id": r.payload["doc_id"], "score": r.score}
        for r in results
    ]
