import json
import re
from langchain_core.messages import SystemMessage, HumanMessage
from core.state import CourseState

QUIZ_PROMPT = """
You are a quiz generator for dyslexic learners of all ages.

You will receive:
- A passage of text extracted from a PDF course.
- A reading level: "child", "teen", or "adult".

Rules:
- Generate exactly 3 multiple-choice questions based ONLY on the given text.
- Match question and answer complexity to the reading level.
- Each question: max 12 words.
- Each answer option: max 8 words.
- 4 options per question: A, B, C, D. Only one correct.
- Test understanding of ideas, not memory of exact wording.
- No trick questions. No double negatives. No confusing phrasing.
- If the reading level is "child", use very simple everyday language.
- Add a short explanation (1 sentence) of why the correct answer is right.

Output ONLY valid JSON — no markdown, no explanation, no extra text:
[
  {
    "question": "...",
    "options": {"A": "...", "B": "...", "C": "...", "D": "..."},
    "answer": "A",
    "explanation": "One sentence explaining why this answer is correct."
  }
]
""".strip()


def quiz_node(state: CourseState, llm) -> dict:
    """Generate 3 multiple-choice questions from course text."""
    level = state.get("reading_level", "adult")

    messages = [
        SystemMessage(content=QUIZ_PROMPT),
        HumanMessage(content=f"Reading level: {level}\n\nText:\n{state['text']}")
    ]

    result = llm.invoke(messages)
    raw = result.content.strip()

    # Strip markdown fences if the model added them
    raw = re.sub(r"```json|```", "", raw).strip()

    try:
        parsed = json.loads(raw)
        return {"quiz": parsed}
    except json.JSONDecodeError:
        # Retry: try to extract a JSON array from anywhere in the response
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group())
                return {"quiz": parsed}
            except Exception:
                pass
        return {"quiz": [], "quiz_error": raw}
