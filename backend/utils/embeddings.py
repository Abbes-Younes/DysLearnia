# Optional: FAISS + embeddings for RAG (e.g. search course chunks)
from typing import List

_embedder = None
_index = None


def get_embedder():
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder


def embed_texts(texts: List[str]) -> List[List[float]]:
    model = get_embedder()
    return model.encode(texts).tolist()


def build_faiss_index(texts: List[str]):
    """Build a FAISS index from a list of text chunks (e.g. simplified course chunks)."""
    import faiss
    vectors = get_embedder().encode(texts)
    vectors = vectors.astype("float32")
    d = vectors.shape[1]
    index = faiss.IndexFlatL2(d)
    index.add(vectors)
    return index


def search_faiss(index, query: str, k: int = 5) -> List[int]:
    """Return indices of k nearest chunks to query."""
    import faiss
    model = get_embedder()
    q = model.encode([query]).astype("float32")
    distances, indices = index.search(q, k)
    return indices[0].tolist()
