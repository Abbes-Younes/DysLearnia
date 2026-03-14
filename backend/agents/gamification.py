import json
import re
from langchain_core.messages import SystemMessage, HumanMessage
from core.state import CourseState

GAMIFICATION_PROMPT = """
You are an encouraging coach for dyslexic learners of all ages.

You will receive a JSON object with the student's progress:
- score: number of correct quiz answers (integer)
- total: total questions attempted (integer)
- streak: number of sessions completed in a row (integer)
- age_group: "child", "teen", or "adult"

Generate:
1. message         — 1 warm, specific motivational sentence. Match tone to age group:
                     child → very enthusiastic, simple words, use their score.
                     teen  → cool, low-key encouragement, not patronising.
                     adult → respectful, matter-of-fact positivity.
2. badge           — A fun 2-3 word badge name they just earned, relevant to score or streak.
3. next_challenge  — 1 short actionable suggestion for what to do next.

Output ONLY valid JSON — no markdown, no explanation, no extra text:
{
  "message": "...",
  "badge": "...",
  "next_challenge": "..."
}
""".strip()


def gamification_node(state: CourseState, llm) -> dict:
    """Generate badge, message, and next challenge based on student progress."""
    progress = state.get("progress") or {
        "score": 0,
        "total": 0,
        "streak": 1,
        "age_group": state.get("reading_level", "adult")
    }

    messages = [
        SystemMessage(content=GAMIFICATION_PROMPT),
        HumanMessage(content=f"Student progress:\n{json.dumps(progress)}")
    ]

    result = llm.invoke(messages)
    raw = result.content.strip()
    raw = re.sub(r"```json|```", "", raw).strip()

    try:
        parsed = json.loads(raw)
        return {"gamification": parsed}
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group())
                return {"gamification": parsed}
            except Exception:
                pass
        return {"gamification": {}, "gamification_error": raw}
