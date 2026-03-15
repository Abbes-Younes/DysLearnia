from langchain_core.prompts import ChatPromptTemplate
from core.state import CourseState
from api.schemas import QuizQuestion
from typing import List
from pydantic import BaseModel, RootModel

QUIZ_PROMPT = """
You are a quiz generator for dyslexic learners of all ages.

You will receive:
- A passage of text extracted from a PDF course.
- A reading level: "child", "teen", or "adult".

Rules:
- Generate exactly 3 multiple-choice questions based ONLY on the given text.
- Match question and answer complexity to the reading level.
- Each question: max 12 words.
- Each answer option: max 8 words.
- 4 options per question: A, B, C, D. Only one correct.
- Test understanding of ideas, not memory of exact wording.
- No trick questions. No double negatives. No confusing phrasing.
- If the reading level is "child", use very simple everyday language.
- Add a short explanation (1 sentence) of why the correct answer is right.
""".strip()

class QuizOutput(BaseModel):
    questions: List[QuizQuestion]

def quiz_node(state: CourseState, llm) -> dict:
    level = state.get("reading_level", "adult")
    text = state.get("text", "")

    prompt = ChatPromptTemplate.from_messages([
        ("system", QUIZ_PROMPT),
        ("human", "Reading level: {level}\n\nText:\n{text}")
    ])
    
    chain = prompt | llm.with_structured_output(QuizOutput)

    try:
        result = chain.invoke({"level": level, "text": text})
        return {"quiz": result.questions, "quiz_error": None}
    except Exception as e:
        return {"quiz": [], "quiz_error": str(e)}
