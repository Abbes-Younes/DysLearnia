from typing import TypedDict, Optional, List

class CourseState(TypedDict):
    # --- inputs ---
    raw_text: str               # from OCR — every agent can read this
    reading_level: str          # "child" | "teen" | "adult"
    user_question: Optional[str]

    # --- agent outputs (each agent writes to its own key) ---
    simplified_text: Optional[str]   # written by: simplifier
    quiz: Optional[List[dict]]       # written by: quiz
    quiz_error: Optional[str]
    hint: Optional[str]              # written by: hint
    gamification: Optional[dict]     # written by: gamification
    gamification_error: Optional[str]

    # --- pipeline metadata ---
    agents_run: Optional[List[str]]  # tracks which agents have run
    progress: Optional[dict]         # for gamification input