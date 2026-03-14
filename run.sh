#!/bin/bash
# Start backend + frontend (set QWEN_MODEL_PATH to your .gguf model first)
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:+$PYTHONPATH:}$(pwd)/backend"
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
