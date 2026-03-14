# Text simplifier agent – dyslexia-friendly simplification using local Qwen 3.5
from typing import Literal

from models.local_llm import get_llm

ReadingLevel = Literal["very_simple", "simple", "standard"]


class TextSimplifierAgent:
    """Simplifies text for dyslexic learners using the local LLM."""

    def __init__(self, level: ReadingLevel = "simple"):
        self.level = level

    def simplify(self, text: str, level: ReadingLevel | None = None) -> str:
        if not (text or "").strip():
            return ""

        level = level or self.level

        if level == "very_simple":
            instructions = (
                "Use very short sentences and common words. "
                "Avoid idioms. Add helpful line breaks."
            )
        elif level == "simple":
            instructions = (
                "Use clear, simple language with short sentences. "
                "Explain difficult words directly after they appear."
            )
        else:
            instructions = (
                "Keep the meaning but make the text easier to read. "
                "Split long sentences and reduce complex clauses."
            )

        prompt = (
            "You are a reading support assistant for dyslexic students. "
            "Simplify the following text so it is easier to read and understand.\n"
            f"{instructions}\n\n"
            "Original text:\n"
            f"{text}\n\n"
            "Simplified version (output only the simplified text, nothing else):\n"
        )

        llm = get_llm()
        return llm.generate(prompt, max_tokens=1024)
