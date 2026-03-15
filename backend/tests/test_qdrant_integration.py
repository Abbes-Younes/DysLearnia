"""
tests/test_qdrant_integration.py — Integration tests for Qdrant db layer.

Requires a running Qdrant instance at http://localhost:6333.
Skip automatically if QDRANT_URL is not set or Qdrant is unreachable.
"""
import os
import uuid

import pytest

# Point at local container
os.environ.setdefault("QDRANT_URL", "http://localhost:6333")
os.environ.pop("QDRANT_API_KEY", None)  # no auth for local


def _qdrant_available() -> bool:
    try:
        import httpx
        r = httpx.get("http://localhost:6333/healthz", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _qdrant_available(),
    reason="Qdrant not reachable at localhost:6333",
)


@pytest.fixture(autouse=True)
def reset_qdrant_client():
    """Reset the cached Qdrant client so env vars are picked up fresh."""
    import db.qdrant as q
    q._client = None
    q._embedder = None
    yield
    q._client = None
    q._embedder = None


# ── ensure_collection ─────────────────────────────────────────────────────────

def test_ensure_collection_creates_collection():
    from db.qdrant import ensure_collection, _get_client, COLLECTION
    ensure_collection()
    client = _get_client()
    names = [c.name for c in client.get_collections().collections]
    assert COLLECTION in names


def test_ensure_collection_idempotent():
    from db.qdrant import ensure_collection
    ensure_collection()
    ensure_collection()  # calling twice should not raise


# ── index_document ────────────────────────────────────────────────────────────

def test_index_document_returns_true():
    from db.qdrant import index_document
    doc_id = f"test-doc-{uuid.uuid4()}"
    chunks = ["The mitochondria is the powerhouse of the cell.",
              "Photosynthesis converts sunlight into glucose."]
    result = index_document(doc_id, "test-user", chunks)
    assert result is True


def test_index_document_multiple_chunks():
    from db.qdrant import index_document, retrieve
    doc_id = f"test-doc-{uuid.uuid4()}"
    chunks = [f"Chunk number {i}: content about topic {i}." for i in range(5)]
    index_document(doc_id, "test-user", chunks)
    results = retrieve(doc_id, "topic", k=5)
    assert len(results) > 0


# ── retrieve ──────────────────────────────────────────────────────────────────

def test_retrieve_returns_relevant_chunks():
    from db.qdrant import index_document, retrieve
    doc_id = f"test-doc-{uuid.uuid4()}"
    chunks = [
        "The heart pumps blood through the circulatory system.",
        "The brain controls all cognitive functions.",
        "The lungs exchange oxygen and carbon dioxide.",
    ]
    index_document(doc_id, "test-user", chunks)
    results = retrieve(doc_id, "heart blood circulation", k=3)
    assert len(results) >= 1
    # The most relevant chunk should mention heart or blood
    assert any("heart" in r.lower() or "blood" in r.lower() for r in results)


def test_retrieve_respects_doc_id_filter():
    from db.qdrant import index_document, retrieve
    doc_a = f"doc-a-{uuid.uuid4()}"
    doc_b = f"doc-b-{uuid.uuid4()}"
    index_document(doc_a, "user1", ["Alpha document: solar energy uses sunlight."])
    index_document(doc_b, "user1", ["Beta document: wind energy uses moving air."])

    results_a = retrieve(doc_a, "energy", k=5)
    results_b = retrieve(doc_b, "energy", k=5)

    # doc_a results should not contain doc_b content
    combined_a = " ".join(results_a)
    assert "Alpha" in combined_a
    assert "Beta" not in combined_a


def test_retrieve_empty_for_unknown_doc():
    from db.qdrant import retrieve
    results = retrieve("nonexistent-doc-id-xyz", "anything", k=5)
    assert results == []


def test_retrieve_k_limits_results():
    from db.qdrant import index_document, retrieve
    doc_id = f"test-doc-{uuid.uuid4()}"
    chunks = [f"Fact {i}: the sky is blue." for i in range(10)]
    index_document(doc_id, "test-user", chunks)
    results = retrieve(doc_id, "sky blue", k=3)
    assert len(results) <= 3


# ── search_all_docs ───────────────────────────────────────────────────────────

def test_search_all_docs_returns_results():
    from db.qdrant import index_document, search_all_docs
    user_id = f"user-{uuid.uuid4()}"
    doc_id = f"doc-{uuid.uuid4()}"
    index_document(doc_id, user_id, [
        "Quantum mechanics describes particle behaviour.",
        "Classical mechanics describes macroscopic objects.",
    ])
    results = search_all_docs(user_id, "mechanics", k=5)
    assert len(results) >= 1
    assert "text" in results[0]
    assert "doc_id" in results[0]
    assert "score" in results[0]


def test_search_all_docs_filters_by_user():
    from db.qdrant import index_document, search_all_docs
    user_a = f"user-a-{uuid.uuid4()}"
    user_b = f"user-b-{uuid.uuid4()}"
    index_document(f"doc-{uuid.uuid4()}", user_a, ["User A only content: glaciers."])
    index_document(f"doc-{uuid.uuid4()}", user_b, ["User B only content: volcanoes."])

    results_a = search_all_docs(user_a, "content", k=10)
    texts_a = " ".join(r["text"] for r in results_a)
    assert "glaciers" in texts_a
    assert "volcanoes" not in texts_a


# ── RAGMixin integration ──────────────────────────────────────────────────────

def test_rag_mixin_retrieve_with_real_qdrant():
    from db.qdrant import index_document
    from mixins.rag_mixin import RAGMixin

    class _Mixin(RAGMixin):
        pass

    mixin = _Mixin()
    doc_id = f"rag-test-{uuid.uuid4()}"
    index_document(doc_id, "test-user", [
        "Osmosis is the movement of water across a membrane.",
        "Diffusion moves particles from high to low concentration.",
    ])

    chunks = mixin._retrieve("water movement", doc_id, k=2)
    assert len(chunks) >= 1
    assert any("osmosis" in c.lower() or "water" in c.lower() for c in chunks)
