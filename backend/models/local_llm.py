# Local LLM – Ollama (default) or GGUF via llama-cpp-python
import os
import sys
import shutil
import logging
import subprocess
import urllib.request
from typing import Optional

logger = logging.getLogger(__name__)

# Ollama API
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3.5")
OLLAMA_AUTO_START = os.getenv("OLLAMA_AUTO_START", "1").lower() in ("1", "true", "yes")
_OLLAMA_PROCESS: Optional[subprocess.Popen] = None


class LocalLLM:
    """
    Uses Ollama by default (model you pulled with `ollama pull qwen3.5`).
    Set OLLAMA_MODEL to your model name (e.g. qwen3.5, qwen2.5).
    Optional: set OLLAMA_BASE_URL if Ollama runs elsewhere.
    Fallback: GGUF file via QWEN_MODEL_PATH / LLAMA_MODEL_PATH with llama-cpp-python.
    """

    def __init__(
        self,
        ollama_base_url: Optional[str] = None,
        ollama_model: Optional[str] = None,
        model_path: Optional[str] = None,
        n_ctx: int = 4096,
        n_batch: int = 512,
    ):
        self.ollama_base_url = (ollama_base_url or OLLAMA_BASE_URL).rstrip("/")
        self.ollama_model = ollama_model or OLLAMA_MODEL
        self.model_path = (
            model_path
            or os.getenv("QWEN_MODEL_PATH")
            or os.getenv("LLAMA_MODEL_PATH")
        )
        self.n_ctx = n_ctx
        self.n_batch = n_batch
        self._llm_cpp = None
        self._use_ollama = True

        # Prefer Ollama if no GGUF path is set
        if self.model_path and os.path.isfile(self.model_path):
            try:
                from llama_cpp import Llama
                self._llm_cpp = Llama(
                    model_path=self.model_path,
                    n_ctx=self.n_ctx,
                    n_batch=self.n_batch,
                    verbose=False,
                )
                self._use_ollama = False
            except Exception as e:
                logger.warning(
                    "Could not load GGUF %s: %s. Using Ollama.",
                    self.model_path,
                    e,
                )
                self._llm_cpp = None
                self._use_ollama = True
        else:
            self._use_ollama = True

        if self._use_ollama and OLLAMA_AUTO_START:
            _ensure_ollama_running(self.ollama_base_url)

    def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.3,
        stop: Optional[list[str]] = None,
    ) -> str:
        """Generate text using Ollama or local GGUF."""
        if self._use_ollama:
            return self._generate_ollama(prompt, max_tokens, temperature, stop)
        if self._llm_cpp is not None:
            return self._generate_llama_cpp(prompt, max_tokens, temperature, stop)
        return _fallback_generate(prompt, max_tokens)

    def _generate_ollama(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        stop: Optional[list[str]],
    ) -> str:
        import json

        url = f"{self.ollama_base_url}/api/generate"
        payload = {
            "model": self.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
            },
        }
        if stop:
            payload["options"]["stop"] = stop

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return (data.get("response") or "").strip()
        except Exception as e:
            if OLLAMA_AUTO_START:
                _ensure_ollama_running(self.ollama_base_url)
                try:
                    with urllib.request.urlopen(req, timeout=120) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                    return (data.get("response") or "").strip()
                except Exception as retry_e:
                    logger.warning("Ollama request failed after start attempt: %s", retry_e)
            else:
                logger.warning("Ollama request failed: %s", e)
            return _fallback_generate(prompt, max_tokens)

    def _generate_llama_cpp(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        stop: Optional[list[str]],
    ) -> str:
        stop = stop or []
        out = self._llm_cpp(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=stop,
            echo=False,
        )
        text = (out.get("choices") or [{}])[0].get("text", "")
        return text.strip()


def _ollama_reachable(base_url: str) -> bool:
    """Return True if Ollama API responds."""
    try:
        req = urllib.request.Request(
            f"{base_url.rstrip('/')}/api/tags",
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=5) as _:
            return True
    except Exception:
        return False


def _ollama_exe() -> Optional[str]:
    """Path to ollama executable (Windows or PATH)."""
    if sys.platform == "win32":
        path = os.path.join(
            os.environ.get("LOCALAPPDATA", ""),
            "Programs",
            "Ollama",
            "ollama.exe",
        )
        if path and os.path.isfile(path):
            return path
    exe = "ollama.exe" if sys.platform == "win32" else "ollama"
    return shutil.which(exe)


def _ensure_ollama_running(base_url: str) -> None:
    """If Ollama is not reachable and OLLAMA_AUTO_START is set, start it once."""
    global _OLLAMA_PROCESS
    if _ollama_reachable(base_url):
        return
    exe = _ollama_exe()
    if not exe:
        logger.warning(
            "Ollama not found. Install from https://ollama.com or run scripts/start_ollama.bat"
        )
        return
    try:
        creationflags = (
            getattr(subprocess, "CREATE_NO_WINDOW", 0) if sys.platform == "win32" else 0
        )
        _OLLAMA_PROCESS = subprocess.Popen(
            [exe, "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creationflags,
        )
        logger.info("Started Ollama server (PID %s). Waiting for it to be ready.", _OLLAMA_PROCESS.pid)
        import time
        for _ in range(30):
            time.sleep(1)
            if _ollama_reachable(base_url):
                return
        logger.warning("Ollama started but not responding yet. Retry in a moment.")
    except Exception as e:
        logger.warning("Could not start Ollama: %s. Run scripts/start_ollama.bat manually.", e)


def _fallback_generate(prompt: str, max_tokens: int) -> str:
    """When Ollama is unreachable or no model is loaded."""
    return (
        "[No model available. Start Ollama (run scripts/start_ollama.bat or ollama serve) "
        "and run: ollama pull qwen3.5. Set OLLAMA_MODEL to your model name.] "
        f"Prompt: {prompt[:max_tokens]}"
    )


_global_llm: Optional[LocalLLM] = None


def get_llm() -> LocalLLM:
    global _global_llm
    if _global_llm is None:
        _global_llm = LocalLLM()
    return _global_llm
