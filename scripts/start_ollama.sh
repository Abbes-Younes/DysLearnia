#!/usr/bin/env bash
# Start Ollama server so Dyslernia can use your local model (e.g. qwen3.5).
# Run this before starting the backend if Ollama is not already running.

if command -v ollama &>/dev/null; then
  echo "Starting Ollama server..."
  ollama serve &
  sleep 3
  echo "Ollama should be running at http://localhost:11434"
else
  echo "Ollama not found. Install from https://ollama.com/download"
  echo "Then run: ollama pull qwen3.5"
  exit 1
fi
