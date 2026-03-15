# Trigger auto-registration of all blocks when this package is imported.
# Import order matters — base must come before registry, registry before blocks.

from blocks.inputs import course_input  # noqa: F401
from blocks.transform import (  # noqa: F401
    summarizer,
    key_concepts,
    flashcards,
    quiz_builder,
    knowledge_graph,
    gap_detector,
    gamification,
    dyslexia_font,
    simplified_text,
    tts_block,
    infographic,
)
from blocks.output.unifiers import (  # noqa: F401
    pdf_unifier,
    pptx_unifier,
    video_unifier,
    audio_unifier,
)
