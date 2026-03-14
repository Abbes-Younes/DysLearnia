from typing import TypedDict, Optional, List


class CourseState(TypedDict):
    # Input
    text: str                        # Extracted PDF text chunk
    task: str                        # "simplify" | "quiz" | "hint" | "gamify"
    reading_level: str               # "child" | "teen" | "adult"
    user_question: Optional[str]     # Used by Hint agent only
    progress: Optional[dict]         # Used by Gamification agent only

    # Outputs (only one will be populated per run)
    simplified_text: Optional[str]
    quiz: Optional[List[dict]]
    quiz_error: Optional[str]
    hint: Optional[str]
    gamification: Optional[dict]
    gamification_error: Optional[str]
