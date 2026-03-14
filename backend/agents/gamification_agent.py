# Gamification agent – points, badges, and optional encouraging messages
from models.local_llm import get_llm


class GamificationAgent:
    """Tracks progress and badges; can generate encouraging messages via LLM."""

    def __init__(self):
        self.points = 0

    def update_progress(self, points_earned: int = 10) -> dict:
        """Add points and return current points and badge."""
        self.points += points_earned
        if self.points >= 100:
            badge = "Champion Reader"
        elif self.points >= 50:
            badge = "Advanced Learner"
        elif self.points >= 20:
            badge = "Rising Star"
        else:
            badge = "Beginner"
        return {
            "points": self.points,
            "badge": badge,
        }

    def get_status(self) -> dict:
        """Return current points and badge without updating."""
        if self.points >= 100:
            badge = "Champion Reader"
        elif self.points >= 50:
            badge = "Advanced Learner"
        elif self.points >= 20:
            badge = "Rising Star"
        else:
            badge = "Beginner"
        return {"points": self.points, "badge": badge}

    def encouraging_message(self, event: str = "completed_lesson") -> str:
        """Optional: one short encouraging sentence from the LLM."""
        prompt = (
            "You are a supportive tutor for a dyslexic student. "
            "Say one short, kind sentence of encouragement (e.g. for completing a lesson). "
            "Do not use emojis. One sentence only.\n"
            f"Event: {event}\n"
            "Encouragement:\n"
        )
        llm = get_llm()
        return llm.generate(prompt, max_tokens=64)
