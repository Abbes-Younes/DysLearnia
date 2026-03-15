from langchain_core.prompts import ChatPromptTemplate
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
    level = state.get("reading_level", "adult")
    text = state.get("simplified_text") or state.get("raw_text", "")
    question = state.get("user_question", "")
    text = state.get("text", "")

    if not question:
        return {"hint": "Please ask a question about the course material.", "hint_error": None}

    prompt = ChatPromptTemplate.from_messages([
        ("system", HINT_PROMPT),
        ("human", "Reading level: {level}\n\nCourse text:\n{text}\n\nStudent question: {question}")
    ])
    
    chain = prompt | llm

    try:
        result = chain.invoke({"level": level, "text": text, "question": question})
        return {"hint": result.content.strip(), "hint_error": None}
    except Exception as e:
        return {"hint": None, "hint_error": str(e)}
