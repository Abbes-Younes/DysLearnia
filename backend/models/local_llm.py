"""
models/local_llm.py — Shared LLM singleton.

Backends (controlled by LLM_BACKEND env var, default "gemini"):
  - "gemini"  — Google Gemini via langchain-google-genai  ← active for testing
  - "ollama"  — local Ollama (commented out below)
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
    backend = os.getenv("LLM_BACKEND", "gemini").lower()

    if backend == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        _llm = ChatGoogleGenerativeAI(
            model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.3,
            max_output_tokens=1024,
        )

    # ── Ollama (local) — uncomment to switch back ──────────────────────────
    # elif backend == "ollama":
    #     from langchain_ollama import ChatOllama
    #     _llm = ChatOllama(
    #         base_url=base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    #         model=model_name or os.getenv("OLLAMA_MODEL", "qwen2.5:3b"),
    #         temperature=0.3,
    #         num_predict=1024,
    #     )
    # ──────────────────────────────────────────────────────────────────────

    else:
        raise ValueError(f"Unknown LLM_BACKEND={backend!r}. Use 'gemini' or 'ollama'.")

    return _llm


def get_llm():
    """Return the singleton LLM, initialising with env vars if not yet done."""
    global _llm
    if _llm is None:
        init_llm()
    return _llm
