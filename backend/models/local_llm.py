"""
models/local_llm.py — Shared LLM singleton.

Backend is controlled by LLM_BACKEND env var (default: "ollama"):
  - "ollama"  — local Ollama (active)
  - "openai"  — OpenAI API (gpt-4o, gpt-4o-mini, etc.)
  - "gemini"  — Google Gemini
"""
from __future__ import annotations

import os

_llm = None


def init_llm(base_url: str | None = None, model_name: str | None = None):
    """Initialise (or re-initialise) the shared LLM singleton."""
    global _llm
    backend = os.getenv("LLM_BACKEND", "ollama").lower()

    if backend == "ollama":
        from langchain_ollama import ChatOllama
        _llm = ChatOllama(
            base_url=base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            model=model_name or os.getenv("OLLAMA_MODEL", "qwen2.5:3b"),
            temperature=0.3,
            num_predict=1024,
        )

    #── Gemini ─────────────────────────────────────────────────────────────
    elif backend == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        _llm = ChatGoogleGenerativeAI(
            model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.3,
            max_output_tokens=1024,
        )

    else:
        raise ValueError(
            f"Unknown LLM_BACKEND={backend!r}. "
            "Supported: 'ollama', 'openai', 'gemini'."
        )

    return _llm


def get_llm():
    """Return the singleton LLM, initialising with env vars if not yet done."""
    global _llm
    if _llm is None:
        init_llm()
    return _llm
