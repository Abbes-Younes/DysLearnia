"""
db/supabase.py — Supabase client singleton (server-side, uses service key).

Gracefully skips operations when SUPABASE_URL is not configured.
"""
from __future__ import annotations

import os
import logging

logger = logging.getLogger(__name__)

_client = None


def get_client():
    global _client
    if _client is not None:
        return _client
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    if not url or not key:
        logger.warning("SUPABASE_URL / SUPABASE_SERVICE_KEY not set — Supabase operations skipped.")
        return None
    try:
        from supabase import create_client
        _client = create_client(url, key)
        return _client
    except ImportError:
        logger.warning("supabase package not installed.")
        return None
    except Exception as exc:
        logger.warning(f"Supabase init error: {exc}")
        return None
