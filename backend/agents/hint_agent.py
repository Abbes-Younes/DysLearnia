# Hint agent – step-by-step hints for dyslexic students using local Qwen 3.5
from models.local_llm import get_llm


class HintAgent:
    """Generates gentle, step-by-step hints without giving the full answer."""

    def generate_hint(
        self,
        question: str,
        student_answer: str | None = None,
    ) -> str:
        if not (question or "").strip():
            return ""

        prompt = (
            "You are a supportive tutor helping a dyslexic student. "
            "Give ONE small, gentle hint—do not give the full answer. "
            "Use short sentences and clear language.\n\n"
            f"Question: {question}\n"
        )
        if student_answer:
            prompt += f"Student's attempt: {student_answer}\n"
        prompt += "\nOne helpful hint only:\n"

        llm = get_llm()
        return llm.generate(prompt, max_tokens=256)
