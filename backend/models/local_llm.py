"""
models/local_llm.py — Shared LangChain-Ollama LLM singleton.

All blocks call get_llm() to access the shared model instance.
init_llm() is called once on app startup with the configured URL/model.
"""
from __future__ import annotations

import os

_llm = None


def init_llm(base_url: str | None = None, model_name: str | None = None):
    """
    Initialise (or re-initialise) the shared LLM.
    Called by the FastAPI lifespan on startup.
    """
    global _llm
    from langchain_ollama import ChatOllama

    _llm = ChatOllama(
        base_url=base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        model=model_name or os.getenv("OLLAMA_MODEL", "qwen2.5:3b"),
        temperature=0.3,
        num_predict=1024,
    )
    return _llm


def get_llm():
    """Return the singleton LLM, initialising with env vars if not yet done."""
    global _llm
    if _llm is None:
        init_llm()
    return _llm
