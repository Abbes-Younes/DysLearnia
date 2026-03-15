from typing import TypedDict, Optional, List
from api.schemas import QuizQuestion, GamificationResponse

class CourseState(TypedDict, total=False):
    # Input
    text: str                        # Extracted PDF text chunk
    task: str                        # "simplify" | "quiz" | "hint" | "gamify"
    reading_level: str               # "child" | "teen" | "adult"
    user_question: Optional[str]     # Used by Hint agent only
    progress: Optional[dict]         # Used by Gamification agent only

    # Outputs (only one will be populated per run)
    simplified_text: Optional[str]
    simplified_text_error: Optional[str]
    quiz: Optional[List[QuizQuestion]]
    quiz_error: Optional[str]
    hint: Optional[str]
    hint_error: Optional[str]
    gamification: Optional[GamificationResponse]
    gamification_error: Optional[str]
