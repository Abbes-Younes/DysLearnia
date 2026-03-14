# Quiz generation agent – creates simple MCQs from passage using local Qwen 3.5
import json
import re
from models.local_llm import get_llm


class QuizAgent:
    """Creates short reading-comprehension quizzes for dyslexic students."""

    def __init__(self, num_questions: int = 3):
        self.num_questions = num_questions

    def generate_quiz(self, passage: str) -> list[dict]:
        """Returns list of {question, options, answer} dicts."""
        if not (passage or "").strip():
            return []

        prompt = (
            "You are creating a short reading quiz for a dyslexic student. "
            "Use clear language and short questions. "
            "Output ONLY a JSON array of objects, each with keys: "
            '"question", "options" (list of 4 strings), "answer" (exact option text).\n'
            f"Create exactly {self.num_questions} multiple-choice questions.\n\n"
            f"Passage:\n{passage}\n\n"
            "JSON array:\n"
        )

        llm = get_llm()
        raw = llm.generate(prompt, max_tokens=600)

        # Try to extract JSON array from response
        try:
            # Handle markdown code blocks
            raw = raw.strip()
            if "```" in raw:
                raw = re.sub(r"^.*?```(?:json)?\s*", "", raw)
                raw = re.sub(r"\s*```.*$", "", raw)
            data = json.loads(raw)
            if isinstance(data, list):
                return [
                    {
                        "question": str(q.get("question", "")),
                        "options": list(q.get("options", [])),
                        "answer": str(q.get("answer", "")),
                    }
                    for q in data
                    if isinstance(q, dict)
                ]
        except (json.JSONDecodeError, TypeError):
            pass
        return []
