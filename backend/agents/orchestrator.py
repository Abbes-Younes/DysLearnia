# Agent orchestrator – LangGraph pipeline: OCR → Simplify → Audio (+ Quiz/Hint/Gamification)
from typing import TypedDict, Any, Optional

from langgraph.graph import StateGraph, END

from agents.ocr_agent import OCRAgent
from agents.text_simplifier import TextSimplifierAgent
from agents.hint_agent import HintAgent
from agents.quiz_agent import QuizAgent
from agents.audio_agent import AudioAgent
from agents.gamification_agent import GamificationAgent


class PipelineState(TypedDict, total=False):
    file_path: str
    raw_text: str
    simplified_text: str
    audio_path: str
    quiz: list
    error: str


def create_pipeline(
    ocr_agent: Optional[OCRAgent] = None,
    simplifier: Optional[TextSimplifierAgent] = None,
    hint_agent: Optional[HintAgent] = None,
    quiz_agent: Optional[QuizAgent] = None,
    audio_agent: Optional[AudioAgent] = None,
    gamification_agent: Optional[GamificationAgent] = None,
):
    """Build the LangGraph pipeline and return compiled app and agents."""
    ocr_agent = ocr_agent or OCRAgent()
    simplifier = simplifier or TextSimplifierAgent()
    hint_agent = hint_agent or HintAgent()
    quiz_agent = quiz_agent or QuizAgent()
    audio_agent = audio_agent or AudioAgent()
    gamification_agent = gamification_agent or GamificationAgent()

    graph = StateGraph(PipelineState)

    def router(state: PipelineState) -> str:
        if state.get("file_path"):
            return "ocr"
        if state.get("raw_text"):
            return "simplify"
        return "end"

    def router_node(state: PipelineState) -> PipelineState:
        """No-op; routing is done via conditional edges."""
        return state

    def ocr_node(state: PipelineState) -> PipelineState:
        try:
            raw = ocr_agent.extract_text(state["file_path"])
            state["raw_text"] = raw
        except Exception as e:
            state["error"] = str(e)
        return state

    def simplify_node(state: PipelineState) -> PipelineState:
        text = state.get("raw_text") or ""
        if not text.strip():
            state["error"] = state.get("error") or "No text to simplify"
            return state
        try:
            state["simplified_text"] = simplifier.simplify(text)
        except Exception as e:
            state["error"] = str(e)
        return state

    def audio_node(state: PipelineState) -> PipelineState:
        text = state.get("simplified_text") or ""
        if not text.strip():
            return state
        try:
            state["audio_path"] = audio_agent.generate_audio(
                text, prefix="course_audio"
            )
        except Exception as e:
            state["error"] = state.get("error") or str(e)
        return state

    graph.add_node("router", router_node)
    graph.add_node("ocr", ocr_node)
    graph.add_node("simplify", simplify_node)
    graph.add_node("audio", audio_node)

    graph.set_entry_point("router")
    graph.add_conditional_edges("router", router, {
        "ocr": "ocr",
        "simplify": "simplify",
        "end": END,
    })
    graph.add_edge("ocr", "simplify")
    graph.add_edge("simplify", "audio")
    graph.add_edge("audio", END)

    app = graph.compile()

    class Orchestrator:
        def __init__(self):
            self.ocr_agent = ocr_agent
            self.simplifier = simplifier
            self.hint_agent = hint_agent
            self.quiz_agent = quiz_agent
            self.audio_agent = audio_agent
            self.gamification_agent = gamification_agent
            self._app = app

        def process_course(
            self,
            file_path: Optional[str] = None,
            raw_text: Optional[str] = None,
        ) -> dict[str, Any]:
            """Run OCR (if file) → simplify → audio. Returns state dict."""
            state: PipelineState = {}
            if file_path:
                state["file_path"] = file_path
            elif raw_text:
                state["raw_text"] = raw_text
            else:
                return {"error": "Provide file_path or raw_text"}
            result = self._app.invoke(state)
            return {
                "raw_text": result.get("raw_text"),
                "simplified_text": result.get("simplified_text"),
                "audio_path": result.get("audio_path"),
                "error": result.get("error"),
            }

        def simplify_text(self, text: str) -> str:
            return self.simplifier.simplify(text)

        def generate_hint(
            self,
            question: str,
            student_answer: Optional[str] = None,
        ) -> str:
            return self.hint_agent.generate_hint(question, student_answer)

        def generate_quiz(self, text: str) -> list:
            return self.quiz_agent.generate_quiz(text)

        def text_to_audio(self, text: str, prefix: str = "lesson_audio") -> str:
            return self.audio_agent.generate_audio(text, prefix=prefix)

        def update_progress(self, points: int = 10) -> dict:
            return self.gamification_agent.update_progress(points)

        def get_progress(self) -> dict:
            return self.gamification_agent.get_status()

    return Orchestrator()


# Singleton for FastAPI
pipeline = create_pipeline()
