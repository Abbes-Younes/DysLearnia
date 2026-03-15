from langchain_core.prompts import ChatPromptTemplate
from core.state import CourseState

SIMPLIFIER_PROMPT = """
You are an accessibility assistant for people with dyslexia of all ages.

You will receive:
- A passage of text extracted from a PDF course.
- A reading level: "child" (age 6-12), "teen" (age 13-18), or "adult".

Your job:
- Rewrite the text so it is easy to read at the given level.
- Use SHORT sentences — maximum 12 words each.
- Replace every technical or difficult word with a simpler one.
  If a term MUST be kept (e.g. a subject keyword), explain it in brackets right after.
- Break text into small paragraphs of 2-3 sentences maximum.
- Use active voice only. Never passive voice.
- Keep ALL the original ideas — do not summarize or remove content.
- Do NOT add bullet points unless the original had them.

Output only the rewritten text. No intro sentence, no explanation.
""".strip()

def simplifier_node(state: CourseState, llm) -> dict:
    level = state.get("reading_level", "adult")
    text = state.get("text", "")

    prompt = ChatPromptTemplate.from_messages([
        ("system", SIMPLIFIER_PROMPT),
        ("human", "Reading level: {level}\n\nText:\n{text}")
    ])
    
    chain = prompt | llm

    try:
        result = chain.invoke({"level": level, "text": text})
        return {"simplified_text": result.content.strip(), "simplified_text_error": None}
    except Exception as e:
        return {"simplified_text": None, "simplified_text_error": str(e)}
