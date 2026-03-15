import json
from langchain_core.prompts import ChatPromptTemplate
from core.state import CourseState
from api.schemas import GamificationResponse

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
""".strip()


def gamification_node(state: CourseState, llm) -> dict:
    """Generate badge, message, and next challenge based on student progress."""
    progress = state.get("progress") or {
        "score": 0,
        "total": 0,
        "streak": 1,
        "age_group": state.get("reading_level", "adult")
    }

    prompt = ChatPromptTemplate.from_messages([
        ("system", GAMIFICATION_PROMPT),
        ("human", "Student progress:\n{progress}")
    ])
    
    chain = prompt | llm.with_structured_output(GamificationResponse)

    try:
        result = chain.invoke({"progress": json.dumps(progress)})
        return {"gamification": result, "gamification_error": None}
    except Exception as e:
        return {"gamification": None, "gamification_error": str(e)}
