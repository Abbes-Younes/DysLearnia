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
    level = state.get("reading_level", "adult")
    # smart input — use simplified if available
    text = state.get("simplified_text") or state.get("raw_text", "")
    print(f"[quiz] input: {len(text)} chars")
    messages = [
        SystemMessage(content=QUIZ_PROMPT),
        HumanMessage(content=f"Reading level: {level}\n\nText:\n{text}")
    ]
    result = llm.invoke(messages)
    raw = re.sub(r"```json|```", "", result.content).strip()
    try:
        return {"quiz": json.loads(raw)}
    except:
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        if match:
            try:
                return {"quiz": json.loads(match.group())}
            except: pass
        return {"quiz": [], "quiz_error": raw}