from functools import partial
from langgraph.graph import StateGraph, END

from core.state import CourseState
from agents.simplifier import simplifier_node
from agents.quiz import quiz_node
from agents.hint import hint_node
from agents.gamification import gamification_node


def build_graph(*_args, **_kwargs) -> object:
    """
    Build and compile the LangGraph agent graph.
    Uses the shared LLM singleton (get_llm()) so the backend
    selected via LLM_BACKEND env var applies here too.
    """
    from models.local_llm import get_llm
    llm = get_llm()

    def _simplifier(state):
        return simplifier_node(state, llm)

    def _quiz(state):
        return quiz_node(state, llm)

    def _hint(state):
        return hint_node(state, llm)

    def _gamification(state):
        return gamification_node(state, llm)

    def _router(state):
        task = state.get("task", "")
        valid = {"simplify", "quiz", "hint", "gamify"}
        if task not in valid:
            raise ValueError(f"Unknown task '{task}'. Must be one of {valid}")
        return task

    graph = StateGraph(CourseState)

    graph.add_node("simplify", _simplifier)
    graph.add_node("quiz",     _quiz)
    graph.add_node("hint",     _hint)
    graph.add_node("gamify",   _gamification)

    graph.set_conditional_entry_point(
        _router,
        {
            "simplify": "simplify",
            "quiz":     "quiz",
            "hint":     "hint",
            "gamify":   "gamify",
        }
    )

    for node in ["simplify", "quiz", "hint", "gamify"]:
        graph.add_edge(node, END)

    return graph.compile()
