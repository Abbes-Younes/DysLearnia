from langchain_core.messages import SystemMessage, HumanMessage
from core.state import CourseState

HINT_PROMPT = """
You are a patient, friendly tutor helping a dyslexic student who is stuck.

You will receive:
- The course text as context.
- The student's question.
- A reading level: "child", "teen", or "adult".

Your response rules:
- Answer in exactly 2 parts:
  1. One clear sentence that directly answers the question.
  2. One concrete real-life example starting with "For example,".
- Adjust vocabulary strictly to the reading level:
  "child"  → words a 6-year-old knows, very short sentences.
  "teen"   → clear everyday language, no jargon.
  "adult"  → plain English, keep technical terms only if unavoidable.
- Total response: under 70 words.
- Never say "Great question!", "As I mentioned", or any filler phrase.
- If the question is not related to the course text, reply with exactly:
  "I can only help with questions about this course material."
""".strip()


def hint_node(state: CourseState, llm) -> dict:
    """Answer a student's question using course text as context."""
    level = state.get("reading_level", "adult")
    question = state.get("user_question", "")

    if not question:
        return {"hint": "Please ask a question about the course material."}

    messages = [
        SystemMessage(content=HINT_PROMPT),
        HumanMessage(content=(
            f"Reading level: {level}\n\n"
            f"Course text:\n{state['text']}\n\n"
            f"Student question: {question}"
        ))
    ]

    result = llm.invoke(messages)
    return {"hint": result.content.strip()}
