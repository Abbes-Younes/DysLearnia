# DysLearnia — Master Project Prompt

> SMU Hackathon 5th Edition · Theme: Education in the Era of Artificial Intelligence  
> Version: 2.0 · Status: Baseline Specification  
> Changes from v1.0: Generic course input block (PDF+PPTX+Video); Qdrant Cloud replaces local ChromaDB; collaboration section rewritten with correct Hocuspocus tooling; output unifier blocks added (PDF, PPTX, Video, Audio)

---

## 1. Project Identity

**Name:** DysLearnia  
**Tagline:** _Your course material, processed your way._  
**Core premise:** An AI-powered learning pipeline builder where students and teachers visually chain processing blocks to transform course content into personalized, accessible formats — with zero dependency on external AI APIs.

DysLearnia is not a chatbot. It is a **visual content transformation engine** where every student configures their own learning pipeline. A dyslexic student chains `PDF → Summarize → Dyslexia Font → TTS`. A visual learner chains `PDF → Key Concepts → Knowledge Graph`. An exam-prepper chains `PDF → Flashcards → Quiz → Gap Analysis`. The pipeline is the product.

---

## 2. Hackathon Alignment

### Challenge tracks addressed (all three, not one)

| Track                               | How DysLearnia addresses it                                                                                 |
| ----------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Adaptive Learning & Personalization | Pipeline builder with per-student saved flows, gap detector block, quiz performance tracking in Supabase    |
| Inclusive Learning for Disabilities | Dyslexia font block, TTS block, simplified text block, voice-driven pipeline builder for motor disabilities |
| Course-Specific AI Tutoring         | RAG-grounded tutor chat block built on ChromaDB + local LLM, all responses cited to source chunks           |

### Judging criteria mapping

| Criterion                          | Weight | DysLearnia answer                                                                                        |
| ---------------------------------- | ------ | -------------------------------------------------------------------------------------------------------- |
| Innovation & Original Thinking     | 15%    | Visual pipeline metaphor applied to learning — no team will bring this                                   |
| AI Integration & Educational Value | 15%    | Every block is an AI task; AI compounds across the pipeline                                              |
| System Architecture                | 10%    | Modular IBlock interface, registry pattern, topological runner — each component has one responsibility   |
| Reliability & Grounded Responses   | 10%    | Qdrant Cloud RAG on every LLM block; `source_chunks` surfaced as citations; hallucination hedge detector |
| Model Compliance                   | 5%     | Qwen2.5-3B via Ollama — fully local, 3B < 5B limit, zero external API calls                              |
| Usability & Learning Experience    | 10%    | Drag-and-drop canvas, voice builder, preset templates, real-time collaboration                           |
| Presentation & Demo                | 15%    | Three live pipelines in 90 seconds: dyslexia → knowledge graph → exam prep                               |

---

## 3. System Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│  Next.js 14 Frontend (App Router)                       │
│  React Flow canvas · Zustand + Yjs · Voice input        │
└────────────────┬───────────────────────────────┬────────┘
                 │ REST + WebSocket               │ WS room
                 ▼                               ▼
┌───────────────────────┐           ┌────────────────────┐
│  FastAPI Backend      │           │  Hocuspocus server │
│  Pipeline runner      │           │  Collab + auth     │
│  Block registry       │           │  (Node.js :4000)   │
│  Speech intent API    │           └────────────────────┘
└──────┬──────┬─────────┘
       │      │
       ▼      ▼
┌──────────┐ ┌──────────────────────────────────────────────────┐
│  Ollama  │ │  Block runners                                   │
│  Qwen2.5 │ │  LLM · Whisper · Kokoro TTS · D3 · MoviePy      │
│  :11434  │ │  python-pptx · WeasyPrint · python-pptx (input) │
└──────────┘ └──────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│  Data layer                                              │
│  Supabase (auth + flows + progress + comments + storage) │
│  Qdrant Cloud (vector store — all embeddings, cloud)     │
│  Neo4j (knowledge graph persistence + traversal)         │
└──────────────────────────────────────────────────────────┘
```

---

## 4. Repository Structure

```
dyslearnia/
├── PROMPT.md                        ← this file
├── docker-compose.yml               ← full stack, one command
├── .env.example
├── README.md
│
├── backend/                         ← FastAPI Python app
│   ├── app.py                       ← existing, extend with new routers
│   ├── agents/                      ← existing agents, refactored as IBlock
│   │   ├── audio_agent.py
│   │   ├── gamification_agent.py
│   │   ├── hint_agent.py
│   │   ├── ocr_agent.py
│   │   ├── orchestrator.py          ← becomes PipelineRunner
│   │   ├── quiz_agent.py
│   │   └── text_simplifier.py
│   ├── blocks/                      ← NEW — IBlock system
│   │   ├── base.py                  ← IBlock ABC + BlockData dataclass
│   │   ├── registry.py              ← @register_block decorator
│   │   ├── inputs/
│   │   │   └── course_input.py      ← GENERIC: handles PDF, PPTX, video
│   │   ├── transform/
│   │   │   ├── summarizer.py        ← wraps existing text_simplifier.py
│   │   │   ├── key_concepts.py
│   │   │   ├── flashcards.py
│   │   │   ├── quiz_builder.py      ← wraps existing quiz_agent.py
│   │   │   ├── knowledge_graph.py   ← Neo4j write + D3 export
│   │   │   ├── gap_detector.py      ← wraps existing hint_agent.py
│   │   │   └── gamification.py      ← wraps existing gamification_agent.py
│   │   └── output/
│   │       ├── tts_block.py         ← wraps existing audio.py → binary/wav
│   │       ├── dyslexia_block.py    ← reformats text as HTML
│   │       ├── infographic.py       ← text → PNG (Pillow + Jinja2)
│   │       ├── simplified_text.py
│   │       └── unifiers/            ← NEW — produce real downloadable files
│   │           ├── pdf_unifier.py   ← text + PNG(s) → PDF via WeasyPrint
│   │           ├── pptx_unifier.py  ← text + PNG(s) → PPTX via python-pptx
│   │           ├── video_unifier.py ← text + PNG(s) + audio → MP4 via MoviePy
│   │           └── audio_unifier.py ← text → WAV/MP3 via Kokoro, concat clips
│   ├── engine/
│   │   ├── runner.py                ← PipelineRunner (topo-sort + async exec)
│   │   ├── validator.py             ← edge type-compatibility checks
│   │   └── events.py               ← WebSocket progress event shapes
│   ├── mixins/
│   │   └── rag_mixin.py             ← Qdrant Cloud retrieval + grounding
│   ├── models/
│   │   └── local_llm.py             ← existing, unchanged
│   ├── routes/
│   │   ├── blocks.py                ← GET /api/blocks (registry dump)
│   │   ├── pipeline.py              ← POST /api/pipeline/run + WS
│   │   ├── flows.py                 ← save/load/fork/templates (Supabase)
│   │   ├── documents.py             ← upload + Qdrant Cloud indexing
│   │   └── speech.py                ← Whisper transcribe + intent parse
│   ├── db/
│   │   ├── supabase.py              ← Supabase client singleton
│   │   ├── qdrant.py                ← Qdrant Cloud client singleton
│   │   └── neo4j.py                 ← Neo4j driver singleton
│   └── utils/
│       ├── audio.py                 ← existing
│       ├── embeddings.py            ← existing, now wraps Qdrant Cloud
│       └── speech_input.py          ← existing
│
├── collab-server/                   ← NEW — Node.js Hocuspocus server
│   ├── server.ts                    ← Hocuspocus with Database + Auth extensions
│   └── package.json
│
└── dyslearnia-front/                ← existing Next.js app, extend
    └── app/
        ├── components/
        │   ├── app-header.tsx        ← existing
        │   ├── course-card.tsx       ← existing
        │   ├── progress-ring.tsx     ← existing
        │   ├── upload-zone.tsx       ← existing
        │   ├── canvas/               ← NEW
        │   │   ├── PipelineCanvas.tsx
        │   │   ├── BlockNode.tsx     ← custom React Flow node
        │   │   └── BlockPalette.tsx  ← drag source sidebar
        │   ├── collaboration/        ← NEW
        │   │   ├── CollaboratorCursors.tsx
        │   │   └── CommentThread.tsx
        │   ├── speech/               ← NEW
        │   │   ├── VoiceButton.tsx
        │   │   └── dispatcher.ts
        │   └── library/              ← NEW
        │       ├── FlowLibrary.tsx
        │       └── TemplateGallery.tsx
        ├── store/                    ← NEW
        │   └── pipeline.ts           ← Zustand + HocuspocusProvider store
        └── pipeline/                 ← NEW route
            └── [id]/
                └── page.tsx
```

---

## 5. Core Abstractions

### 5.1 BlockData — the envelope passed between every block

```python
# backend/blocks/base.py
from dataclasses import dataclass, field
from typing import Any

@dataclass
class BlockData:
    text: str | None = None           # main text payload
    binary: bytes | None = None       # audio (wav), image (png), video (mp4)
    mime_type: str | None = None      # "audio/wav" | "text/html" | "image/png"
    metadata: dict[str, Any] = field(default_factory=dict)
    # metadata keys (non-exhaustive):
    #   confidence: float       — hallucination score 0.0–1.0
    #   word_count: int
    #   reading_level: str      — A1/A2/B1/B2/C1/C2
    #   graph_nodes: int        — for knowledge graph blocks
    #   audio_duration_s: float
    source_chunks: list[str] = field(default_factory=list)
    # the RAG excerpts that grounded this output — shown as citations in UI
```

### 5.2 IBlock — every processing node implements this

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class BlockDescription:
    name: str               # machine key: "summarizer"
    display_name: str       # UI label: "Summarizer"
    group: str              # "input" | "transform" | "output" | "intelligence"
    input_types: list[str]  # ["text"] | ["binary/audio"] | ["text", "binary/pdf"]
    output_types: list[str] # ["text"] | ["binary/audio"] | ["graph"]
    parameters: list[dict]  # schema rendered by frontend into sliders/selects

class IBlock(ABC):
    description: BlockDescription

    @abstractmethod
    async def execute(
        self,
        inputs: list[BlockData],
        params: dict[str, Any]
    ) -> list[BlockData]:
        ...
```

### 5.3 Block registry — auto-discovery via decorator

```python
# backend/blocks/registry.py
BLOCK_REGISTRY: dict[str, type[IBlock]] = {}

def register_block(cls: type[IBlock]) -> type[IBlock]:
    BLOCK_REGISTRY[cls.description.name] = cls
    return cls

# GET /api/blocks returns:
# [{ name, display_name, group, input_types, output_types, parameters }, ...]
# Frontend uses this to render the palette and validate edge connections.
```

### 5.4 Pipeline runner — topological execution with live WebSocket events

```python
# backend/engine/runner.py
class PipelineRunner:
    """
    Accepts a pipeline definition (nodes + edges + params),
    executes blocks in dependency order,
    streams progress events via progress_cb.
    Equivalent to n8n's WorkflowExecute but stripped to educational domain.
    """
    async def execute(
        self,
        params: dict[str, dict],
        progress_cb: Callable[[str, str, list[BlockData] | None], Awaitable]
    ) -> dict[str, list[BlockData]]:
        order = self._topological_sort()
        for node_id in order:
            await progress_cb(node_id, "running", None)
            inputs = self._collect_inputs(node_id)
            result = await self.blocks[node_id].execute(inputs, params.get(node_id, {}))
            self.run_data[node_id] = result
            await progress_cb(node_id, "done", result)
        return self._terminal_outputs()
```

### 5.5 RAG mixin — every LLM block inherits this

```python
# backend/mixins/rag_mixin.py
class RAGMixin:
    def _retrieve(self, query: str, doc_id: str, k: int = 5) -> list[str]:
        """Embed query, retrieve top-k chunks from Qdrant Cloud."""
        from db.qdrant import retrieve
        return retrieve(doc_id, query, k)

    def _grounded_prompt(self, task: str, chunks: list[str]) -> str:
        """
        Wraps task in a strict grounding instruction:
        'Use ONLY the following excerpts. If you cannot complete the task
        from the excerpts alone, say [INSUFFICIENT CONTEXT].'
        """

    def _confidence_score(self, output: str) -> float:
        """
        Detects ungrounded hedges: 'generally', 'typically', 'I think', etc.
        Returns 0.0–1.0. Low score = yellow warning badge in UI.
        """
```

---

## 6. Block Catalogue

### Input block (single generic block replaces all per-format inputs)

| Block        | Key            | Accepted formats                                 | Output                       | Notes                                                                                                |
| ------------ | -------------- | ------------------------------------------------ | ---------------------------- | ---------------------------------------------------------------------------------------------------- |
| Course input | `course_input` | `.pdf`, `.pptx`, `.mp4`, `.mov`, `.mkv`, `.webm` | `text` + `metadata.slides[]` | Auto-detects format; dispatches to correct extractor; chunks and indexes into Qdrant Cloud on upload |

**How `course_input` dispatches internally:**

```python
# backend/blocks/inputs/course_input.py
@register_block
class CourseInputBlock(IBlock, RAGMixin):
    description = BlockDescription(
        name="course_input",
        display_name="Course material",
        group="input",
        input_types=[],
        output_types=["text"],
        parameters=[
            {"name": "language", "type": "select",
             "options": ["auto", "en", "fr", "ar"], "default": "auto"},
            {"name": "extract_images", "type": "toggle", "default": True,
             "label": "Extract embedded images for infographic blocks"},
        ]
    )

    async def execute(self, inputs: list[BlockData], params: dict) -> list[BlockData]:
        file_bytes = inputs[0].binary
        mime = inputs[0].mime_type

        if mime == "application/pdf":
            text, images = self._extract_pdf(file_bytes)
        elif mime in ("application/vnd.openxmlformats-officedocument"
                      ".presentationml.presentation",):
            text, images = self._extract_pptx(file_bytes)
        elif mime.startswith("video/"):
            text, images = await self._extract_video(file_bytes, params.get("language", "auto"))
        else:
            raise ValueError(f"Unsupported MIME type: {mime}")

        doc_id = self._index_to_qdrant(text)   # chunk + embed + upsert
        return [BlockData(
            text=text,
            metadata={
                "doc_id": doc_id,
                "slide_images": images,   # list of base64 PNGs, one per slide/page
                "page_count": len(images),
            }
        )]

    def _extract_pdf(self, data: bytes) -> tuple[str, list[bytes]]:
        # PyMuPDF: extract text + render each page as PNG
        import fitz
        doc = fitz.open(stream=data, filetype="pdf")
        text = "\n\n".join(page.get_text() for page in doc)
        images = [page.get_pixmap(dpi=150).tobytes("png") for page in doc]
        return text, images

    def _extract_pptx(self, data: bytes) -> tuple[str, list[bytes]]:
        # python-pptx for text + slide thumbnails via LibreOffice headless
        import io
        from pptx import Presentation
        prs = Presentation(io.BytesIO(data))
        slide_texts = []
        for slide in prs.slides:
            slide_text = []
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    slide_text.append(shape.text.strip())
            slide_texts.append("\n".join(slide_text))
        text = "\n\n---\n\n".join(slide_texts)
        # Convert slides to PNG thumbnails via LibreOffice (available in Docker image)
        images = self._pptx_to_images(data)
        return text, images

    async def _extract_video(self, data: bytes, lang: str) -> tuple[str, list[bytes]]:
        # faster-whisper for transcript; ffmpeg for keyframe thumbnails
        import tempfile, subprocess
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            f.write(data); tmp_path = f.name
        segments, _ = whisper_model.transcribe(tmp_path, language=None if lang == "auto" else lang)
        text = " ".join(s.text for s in segments)
        # Extract 1 keyframe per 60s of video as PNG thumbnail
        images = self._extract_keyframes(tmp_path)
        return text, images
```

### Transform blocks

| Block           | Key               | Input               | Output       | Parameters                                      |
| --------------- | ----------------- | ------------------- | ------------ | ----------------------------------------------- |
| Summarizer      | `summarizer`      | text                | text         | ratio (0.1–0.9), style (bullets/paragraph/tldr) |
| Key concepts    | `key_concepts`    | text                | text         | max_concepts (5–30)                             |
| Knowledge graph | `knowledge_graph` | text                | graph + text | depth (1–3), min_confidence                     |
| Flashcard gen   | `flashcards`      | text                | text         | count (5–50), difficulty                        |
| Quiz builder    | `quiz_builder`    | text                | text         | count, types (MCQ/short/true-false)             |
| Gap detector    | `gap_detector`    | text + quiz_results | text         | threshold                                       |
| Simplified text | `simplified_text` | text                | text         | level (A1–C2)                                   |
| Gamification    | `gamification`    | quiz_results        | text         | xp_multiplier                                   |
| Dyslexia font   | `dyslexia_font`   | text                | text/html    | font, spacing, line_height                      |
| Infographic     | `infographic`     | text                | binary/png   | theme, columns                                  |
| TTS             | `tts`             | text                | binary/wav   | speed (0.5–2.0), voice                          |
| Tutor chat      | `tutor_chat`      | text                | interactive  | — (terminal block)                              |

### Output unifier blocks (NEW — produce real downloadable files)

These are **terminal blocks** — they accept the accumulated outputs of all upstream blocks and render a single downloadable file. They are the last node in any pipeline that needs a persistent artifact.

| Block         | Key             | Accepted inputs                                    | Output file | Tooling                                                                              |
| ------------- | --------------- | -------------------------------------------------- | ----------- | ------------------------------------------------------------------------------------ |
| PDF unifier   | `pdf_unifier`   | text (markdown) + binary/png (infographics)        | `.pdf`      | `markdown` → HTML via `python-markdown`, images embedded, rendered by **WeasyPrint** |
| PPTX unifier  | `pptx_unifier`  | text (slide content) + binary/png (images)         | `.pptx`     | **python-pptx**: one slide per content section, images on image slides               |
| Video unifier | `video_unifier` | binary/png (slide frames) + binary/wav (TTS audio) | `.mp4`      | **MoviePy v2**: `ImageClip` sequence + `AudioFileClip`, written with `libx264/aac`   |
| Audio unifier | `audio_unifier` | text sections or binary/wav clips                  | `.mp3`      | **Kokoro-82M** for synthesis; **pydub** for concatenation + normalization            |

---

### 6a. Output unifier implementation details

#### PDF unifier — `WeasyPrint` pipeline

```python
# backend/blocks/output/unifiers/pdf_unifier.py
import markdown
from weasyprint import HTML, CSS
from io import BytesIO

@register_block
class PDFUnifierBlock(IBlock):
    description = BlockDescription(
        name="pdf_unifier", display_name="Export as PDF",
        group="output", input_types=["text", "binary/png"], output_types=["binary/pdf"],
        parameters=[
            {"name": "font_size", "type": "slider", "min": 10, "max": 20, "default": 13},
            {"name": "include_toc", "type": "toggle", "default": True},
            {"name": "theme",       "type": "select", "options": ["clean", "dyslexia", "dark"], "default": "clean"},
        ]
    )

    async def execute(self, inputs: list[BlockData], params: dict) -> list[BlockData]:
        # Collect text sections (markdown) and PNG bytes (infographics)
        md_parts = [bd.text for bd in inputs if bd.text]
        png_parts = [bd.binary for bd in inputs if bd.mime_type == "image/png"]

        # 1. Parse markdown → HTML
        full_md = "\n\n---\n\n".join(md_parts)
        body_html = markdown.markdown(full_md, extensions=["tables", "fenced_code", "toc"])

        # 2. Embed infographic PNGs as base64 <img> tags at end of document
        import base64
        img_tags = "".join(
            f'<figure><img src="data:image/png;base64,{base64.b64encode(png).decode()}" '
            f'style="max-width:100%;page-break-inside:avoid"/></figure>'
            for png in png_parts
        )

        # 3. Wrap in full HTML with print CSS
        theme_css = self._get_theme_css(params.get("theme", "clean"), params.get("font_size", 13))
        html = f"""<!DOCTYPE html><html><head>
            <meta charset="utf-8"/>
            <style>{theme_css}</style>
        </head><body>{body_html}{img_tags}</body></html>"""

        # 4. Render to PDF bytes with WeasyPrint
        pdf_bytes = HTML(string=html, base_url="").write_pdf()
        return [BlockData(binary=pdf_bytes, mime_type="application/pdf",
                          metadata={"filename": "dyslearnia_export.pdf"})]

    def _get_theme_css(self, theme: str, font_size: int) -> str:
        base = f"""
            @page {{ margin: 2cm; }}
            body {{ font-size: {font_size}pt; line-height: 1.7; font-family: Georgia, serif; }}
            h1, h2, h3 {{ font-family: Arial, sans-serif; }}
            img {{ max-width: 100%; }}
            table {{ border-collapse: collapse; width: 100%; }}
            td, th {{ border: 1px solid #ccc; padding: 6px; }}
            pre {{ background: #f4f4f4; padding: 1em; border-radius: 4px; }}
            hr {{ border: none; border-top: 1px solid #ddd; margin: 2em 0; }}
        """
        if theme == "dyslexia":
            base += "body { font-family: OpenDyslexic, Arial; letter-spacing: 0.1em; line-height: 2; }"
        return base
```

#### PPTX unifier — `python-pptx` pipeline

```python
# backend/blocks/output/unifiers/pptx_unifier.py
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from io import BytesIO
import re

@register_block
class PPTXUnifierBlock(IBlock):
    description = BlockDescription(
        name="pptx_unifier", display_name="Export as PowerPoint",
        group="output", input_types=["text", "binary/png"], output_types=["binary/pptx"],
        parameters=[
            {"name": "theme_color", "type": "color",  "default": "#2D4A8A"},
            {"name": "font",        "type": "select",
             "options": ["Calibri", "Arial", "OpenDyslexic"], "default": "Calibri"},
            {"name": "layout",      "type": "select",
             "options": ["title_content", "image_right", "full_image"], "default": "title_content"},
        ]
    )

    async def execute(self, inputs: list[BlockData], params: dict) -> list[BlockData]:
        prs = Presentation()
        # 16:9 widescreen
        prs.slide_width  = Inches(13.33)
        prs.slide_height = Inches(7.5)

        color_hex = params.get("theme_color", "#2D4A8A").lstrip("#")
        accent = RGBColor(int(color_hex[0:2],16), int(color_hex[2:4],16), int(color_hex[4:6],16))
        font = params.get("font", "Calibri")

        text_blocks = [bd.text for bd in inputs if bd.text]
        png_blocks  = [bd.binary for bd in inputs if bd.mime_type == "image/png"]

        # Split text by markdown H2 headings — each heading → one slide
        combined = "\n\n".join(text_blocks)
        sections = re.split(r"^#{1,2} (.+)$", combined, flags=re.MULTILINE)

        # First section: title slide
        slide = prs.slides.add_slide(prs.slide_layouts[0])
        slide.shapes.title.text = sections[0].strip()[:80] or "DysLearnia Export"
        if slide.placeholders[1]:
            slide.placeholders[1].text = "Generated by DysLearnia"

        # Remaining sections: content slides
        for i in range(1, len(sections), 2):
            heading = sections[i] if i < len(sections) else ""
            body    = sections[i+1].strip() if i+1 < len(sections) else ""
            slide   = prs.slides.add_slide(prs.slide_layouts[1])  # title + content
            slide.shapes.title.text = heading[:80]
            tf = slide.placeholders[1].text_frame
            tf.text = ""
            for line in body.split("\n"):
                line = line.strip().lstrip("- •").strip()
                if not line: continue
                p = tf.add_paragraph()
                p.text = line
                p.font.size = Pt(16)
                p.font.name = font

        # Append infographic slides (one PNG per slide, full-bleed)
        for png_bytes in png_blocks:
            slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
            with BytesIO(png_bytes) as img_io:
                slide.shapes.add_picture(img_io, Inches(0), Inches(0),
                                         width=prs.slide_width, height=prs.slide_height)

        out = BytesIO()
        prs.save(out)
        return [BlockData(binary=out.getvalue(),
                          mime_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                          metadata={"filename": "dyslearnia_export.pptx"})]
```

#### Video unifier — `MoviePy v2` pipeline

```python
# backend/blocks/output/unifiers/video_unifier.py
# MoviePy v2 API — note: v2 introduced breaking changes from v1
from moviepy import ImageClip, AudioFileClip, CompositeVideoClip, TextClip
from moviepy import concatenate_videoclips
import tempfile, os

@register_block
class VideoUnifierBlock(IBlock):
    description = BlockDescription(
        name="video_unifier", display_name="Export as Video",
        group="output", input_types=["binary/png", "binary/wav"], output_types=["binary/mp4"],
        parameters=[
            {"name": "seconds_per_slide", "type": "slider", "min": 3, "max": 30, "default": 8},
            {"name": "resolution",        "type": "select",
             "options": ["1280x720", "1920x1080"], "default": "1280x720"},
            {"name": "fps",               "type": "select",
             "options": ["24", "30"], "default": "24"},
            {"name": "show_captions",     "type": "toggle", "default": True},
        ]
    )

    async def execute(self, inputs: list[BlockData], params: dict) -> list[BlockData]:
        png_inputs = [bd for bd in inputs if bd.mime_type == "image/png"]
        wav_inputs = [bd for bd in inputs if bd.mime_type == "audio/wav"]
        text_inputs = [bd for bd in inputs if bd.text]

        secs = params.get("seconds_per_slide", 8)
        fps  = int(params.get("fps", 24))
        w, h = (int(x) for x in params.get("resolution", "1280x720").split("x"))

        with tempfile.TemporaryDirectory() as tmp:
            clips = []
            for i, png_bd in enumerate(png_inputs):
                img_path = os.path.join(tmp, f"slide_{i}.png")
                with open(img_path, "wb") as f: f.write(png_bd.binary)

                # Duration: use audio length if available, else fixed seconds
                clip = ImageClip(img_path).with_duration(secs).resized((w, h))

                # Optional caption overlay from paired text block
                if params.get("show_captions") and i < len(text_inputs):
                    caption = text_inputs[i].text[:120] if text_inputs[i].text else ""
                    txt = (TextClip(caption, font_size=24, color="white",
                                    bg_color="rgba(0,0,0,0.5)", size=(w-40, None))
                           .with_position(("center", h - 100))
                           .with_duration(secs))
                    clip = CompositeVideoClip([clip, txt])

                clips.append(clip)

            video = concatenate_videoclips(clips, method="compose")

            # Attach TTS audio if available
            if wav_inputs:
                wav_path = os.path.join(tmp, "narration.wav")
                with open(wav_path, "wb") as f: f.write(wav_inputs[0].binary)
                audio = AudioFileClip(wav_path)
                video = video.with_audio(audio)

            out_path = os.path.join(tmp, "output.mp4")
            video.write_videofile(out_path, fps=fps, codec="libx264",
                                  audio_codec="aac", preset="ultrafast",
                                  ffmpeg_params=["-pix_fmt", "yuv420p"])
            with open(out_path, "rb") as f: mp4_bytes = f.read()

        return [BlockData(binary=mp4_bytes, mime_type="video/mp4",
                          metadata={"filename": "dyslearnia_export.mp4"})]
```

#### Audio unifier — Kokoro + pydub pipeline

```python
# backend/blocks/output/unifiers/audio_unifier.py
from pydub import AudioSegment
from io import BytesIO

@register_block
class AudioUnifierBlock(IBlock):
    description = BlockDescription(
        name="audio_unifier", display_name="Export as Audio",
        group="output", input_types=["text", "binary/wav"], output_types=["binary/mp3"],
        parameters=[
            {"name": "speed",  "type": "slider", "min": 0.5, "max": 2.0, "default": 1.0},
            {"name": "voice",  "type": "select",
             "options": ["warm_female", "neutral_male", "clear_female"], "default": "warm_female"},
            {"name": "silence_between_s", "type": "slider", "min": 0, "max": 3, "default": 0.5},
        ]
    )

    async def execute(self, inputs: list[BlockData], params: dict) -> list[BlockData]:
        silence_ms = int(params.get("silence_between_s", 0.5) * 1000)
        pause = AudioSegment.silent(duration=silence_ms)
        combined = AudioSegment.empty()

        for bd in inputs:
            if bd.binary and bd.mime_type == "audio/wav":
                # Already rendered WAV from upstream TTS block — just append
                seg = AudioSegment.from_wav(BytesIO(bd.binary))
            elif bd.text:
                # Raw text — synthesize via Kokoro
                wav_bytes = await kokoro_synthesize(
                    bd.text,
                    speed=params.get("speed", 1.0),
                    voice=params.get("voice", "warm_female")
                )
                seg = AudioSegment.from_wav(BytesIO(wav_bytes))
            else:
                continue
            combined = combined + seg + pause

        # Normalize and export as MP3
        combined = combined.normalize()
        out = BytesIO()
        combined.export(out, format="mp3", bitrate="128k")
        return [BlockData(binary=out.getvalue(), mime_type="audio/mpeg",
                          metadata={"filename": "dyslearnia_export.mp3",
                                    "duration_s": len(combined) / 1000})]
```

### Edge type compatibility rules

```
text          → summarizer, key_concepts, knowledge_graph, flashcards,
                quiz_builder, simplified_text, dyslexia_font, tts,
                infographic, pdf_unifier, pptx_unifier, audio_unifier
binary/png    → pdf_unifier, pptx_unifier, video_unifier
binary/wav    → video_unifier, audio_unifier
graph         → tutor_chat (graph-aware Cypher queries)
binary/*      → player output blocks only (inline preview in canvas)
```

The frontend enforces this at draw time: incompatible edge = red snap + tooltip explaining the mismatch.

---

## 7. Data Layer

### 7.1 Supabase — auth, flows, progress, comments

Supabase handles authentication (existing `lib/supabase/`) and all relational persistence.

```sql
-- Flows (saved pipelines)
create table flows (
  id            uuid primary key default gen_random_uuid(),
  owner_id      uuid references auth.users not null,
  title         text not null,
  description   text,
  thumbnail     text,                    -- base64 PNG canvas snapshot
  graph         jsonb not null,          -- { nodes, edges } pipeline definition
  is_template   boolean default false,   -- teacher-promoted
  is_public     boolean default false,
  locked_params jsonb default '{}',      -- teacher-locked param keys per node_id
  forked_from   uuid references flows(id),
  created_at    timestamptz default now(),
  updated_at    timestamptz default now()
);

-- Flow tags (for template gallery filtering)
create table flow_tags (
  flow_id uuid references flows(id) on delete cascade,
  tag     text not null,               -- "dyslexia", "exam-prep", "visual", "audio"
  primary key (flow_id, tag)
);

-- Per-node output cache (so re-runs don't reprocess unchanged upstream nodes)
create table pipeline_runs (
  id          uuid primary key default gen_random_uuid(),
  flow_id     uuid references flows(id),
  user_id     uuid references auth.users,
  run_data    jsonb,                   -- { node_id: BlockData }
  completed_at timestamptz
);

-- Student progress (quiz scores, XP, streaks)
create table student_progress (
  user_id       uuid references auth.users primary key,
  xp            integer default 0,
  streak_days   integer default 0,
  last_active   date,
  knowledge_gaps jsonb default '[]'   -- array of { topic, score, detected_at }
);

-- Collaboration comments pinned to nodes
create table node_comments (
  id           uuid primary key default gen_random_uuid(),
  flow_id      uuid references flows(id),
  node_id      text not null,
  author_id    uuid references auth.users,
  author_role  text check (author_role in ('student','teacher')),
  body         text not null,
  resolved     boolean default false,
  created_at   timestamptz default now()
);

-- Row-level security: users see only their own flows + public/template flows
alter table flows enable row level security;
create policy "owner or public" on flows
  for select using (owner_id = auth.uid() or is_public = true or is_template = true);
create policy "owner write" on flows
  for all using (owner_id = auth.uid());
```

**Supabase Realtime** is used for comment notifications — when a teacher adds a comment to a student's flow, Supabase broadcasts a `node_comments` INSERT event to the student's browser without polling.

**Supabase Storage** bucket `course-files` stores raw uploads. The backend fetches the file bytes on pipeline run, processes in memory, and never writes to local disk.

### 7.2 Qdrant Cloud — all vector embeddings (single service, no local ChromaDB)

All embeddings live in **Qdrant Cloud** (free tier: 1GB, sufficient for a hackathon). There is no local ChromaDB container. The single `course_chunks` collection handles both per-document RAG (filtered by `doc_id`) and cross-document search (filtered by `user_id`).

```python
# backend/db/qdrant.py
import os
from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams, Distance, PointStruct,
    Filter, FieldCondition, MatchValue
)
from sentence_transformers import SentenceTransformer

# Qdrant Cloud — credentials from environment
client = QdrantClient(
    url=os.environ["QDRANT_URL"],        # e.g. https://xyz.qdrant.io:6333
    api_key=os.environ["QDRANT_API_KEY"]
)
embedder = SentenceTransformer("all-MiniLM-L6-v2")  # 22MB, local inference

COLLECTION = "course_chunks"

def ensure_collection():
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION not in existing:
        client.create_collection(COLLECTION, vectors_config=VectorParams(
            size=384,            # all-MiniLM-L6-v2 output dimension
            distance=Distance.COSINE
        ))

def index_document(doc_id: str, user_id: str, chunks: list[str]):
    """Chunk a document and upsert all vectors into Qdrant Cloud."""
    ensure_collection()
    points = [
        PointStruct(
            id=abs(hash(f"{doc_id}:{i}")) % (2**63),
            vector=embedder.encode(chunk).tolist(),
            payload={"doc_id": doc_id, "user_id": user_id, "text": chunk, "chunk_index": i}
        )
        for i, chunk in enumerate(chunks)
    ]
    client.upsert(COLLECTION, points=points)

def retrieve(doc_id: str, query: str, k: int = 5) -> list[str]:
    """Per-document RAG — called by RAGMixin for every LLM block."""
    results = client.search(
        COLLECTION, query_vector=embedder.encode(query).tolist(), limit=k,
        query_filter=Filter(must=[FieldCondition(key="doc_id", match=MatchValue(value=doc_id))])
    )
    return [r.payload["text"] for r in results]

def search_all_docs(user_id: str, query: str, k: int = 10) -> list[dict]:
    """Cross-document search — used by tutor_chat and gap_detector."""
    results = client.search(
        COLLECTION, query_vector=embedder.encode(query).tolist(), limit=k,
        query_filter=Filter(must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))])
    )
    return [{"text": r.payload["text"], "doc_id": r.payload["doc_id"], "score": r.score}
            for r in results]
```

The `RAGMixin._retrieve()` calls `qdrant.retrieve()` directly — no ChromaDB anywhere in the stack.

### 7.3 Neo4j — knowledge graph persistence and traversal

Used exclusively by the `knowledge_graph` block (writes triples) and the `tutor_chat` block (Cypher queries for concept neighborhoods and prerequisite chains).

```python
# backend/db/neo4j.py
from neo4j import AsyncGraphDatabase

driver = AsyncGraphDatabase.driver("bolt://neo4j:7687", auth=("neo4j", "dyslearnia"))

async def upsert_graph(doc_id: str, triples: list[tuple[str, str, str]]):
    async with driver.session() as s:
        for subj, rel, obj in triples:
            await s.run("""
                MERGE (a:Concept {name: $subj, doc_id: $doc_id})
                MERGE (b:Concept {name: $obj,  doc_id: $doc_id})
                MERGE (a)-[r:RELATION {type: $rel}]->(b)
            """, subj=subj, obj=obj, rel=rel, doc_id=doc_id)

async def get_neighborhood(concept: str, doc_id: str, depth: int = 2) -> dict:
    async with driver.session() as s:
        result = await s.run("""
            MATCH path = (c:Concept {name: $concept, doc_id: $doc_id})-[*1..$depth]-()
            RETURN path
        """, concept=concept, doc_id=doc_id, depth=depth)
        return _path_to_d3(await result.data())
```

**Why Neo4j:** Cypher prerequisite-chain queries (`MATCH path = (a)-[:RELATION*]->(b)`) find all upstream concepts a student needs to master before understanding a target concept. Neo4j Browser (port 7474) is a free visual demo tool judges can explore during the presentation.

---

## 8. Real-time Collaboration (Yjs + Hocuspocus)

### Why Hocuspocus, not raw y-websocket

The original spec used `y-websocket`. The correct tool is **Hocuspocus** (`@hocuspocus/server`), which is a production-grade Yjs WebSocket backend that adds three things `y-websocket` lacks out of the box:

1. **Authentication hook** (`onAuthenticate`) — verifies the Supabase JWT before the client can read or write the document. `y-websocket` has no built-in auth; you would have to build it manually.
2. **Persistence extension** (`@hocuspocus/extension-database`) — reads the Yjs binary state on connect, writes it on disconnect, via a simple `fetch` / `store` callback. No manual flush timer needed.
3. **Hooks for server-side logic** — `onConnect`, `onChange`, `onDisconnect` let you enforce per-document access control (e.g. read-only for non-owners).

`y-websocket` is still the **client-side provider** on the frontend (`y-websocket` npm package). Hocuspocus is a drop-in replacement server that is wire-compatible with `y-websocket`'s client protocol.

### Hocuspocus server setup

```typescript
// collab-server/server.ts
import { Server } from "@hocuspocus/server";
import { Database } from "@hocuspocus/extension-database";
import { Logger } from "@hocuspocus/extension-logger";
import { createClient } from "@supabase/supabase-js";

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_KEY!, // service role — bypasses RLS for doc storage
);

const server = Server.configure({
  port: 4000,

  // ── Auth ──────────────────────────────────────────────────────
  // Called before any document access. Throw to reject.
  // `data.token` is the Supabase access_token sent by the frontend.
  async onAuthenticate(data) {
    const {
      data: { user },
      error,
    } = await supabase.auth.getUser(data.token);
    if (error || !user) throw new Error("Unauthorized");

    // Attach user info to connection context — available in all other hooks
    return {
      userId: user.id,
      userName: user.user_metadata?.full_name ?? "Student",
    };
  },

  // ── Per-document access control ───────────────────────────────
  // `data.documentName` is the room name sent by the client, e.g. "flow:uuid"
  async onConnect(data) {
    const flowId = data.documentName.replace("flow:", "");
    const { data: flow } = await supabase
      .from("flows")
      .select("owner_id, is_public")
      .eq("id", flowId)
      .single();

    const userId = (data.context as any).userId;
    if (!flow) throw new Error("Flow not found");
    if (flow.owner_id !== userId && !flow.is_public) {
      throw new Error("Access denied");
    }
  },

  extensions: [
    new Logger(),

    // ── Persistence ───────────────────────────────────────────
    // Stores the Yjs document as a binary blob in Supabase.
    // `fetch` is called on first client connect to load initial state.
    // `store` is called after every debounced change (default: 2s debounce).
    new Database({
      async fetch({ documentName }) {
        const flowId = documentName.replace("flow:", "");
        const { data } = await supabase
          .from("flows")
          .select("yjs_state")
          .eq("id", flowId)
          .single();
        // yjs_state is a base64-encoded Uint8Array of the Yjs update
        return data?.yjs_state ? Buffer.from(data.yjs_state, "base64") : null;
      },

      async store({ documentName, state }) {
        const flowId = documentName.replace("flow:", "");
        await supabase
          .from("flows")
          .update({ yjs_state: Buffer.from(state).toString("base64") })
          .eq("id", flowId);
      },
    }),
  ],
});

server.listen();
```

Add `yjs_state bytea` column to the `flows` table:

```sql
alter table flows add column yjs_state text; -- base64-encoded Yjs Uint8Array
```

### Frontend — HocuspocusProvider replaces y-websocket

```typescript
// store/pipeline.ts
import { HocuspocusProvider } from "@hocuspocus/provider";
import * as Y from "yjs";
import { IndexeddbPersistence } from "y-indexeddb"; // offline support

export function createCollabSession(flowId: string, supabaseToken: string) {
  const ydoc = new Y.Doc();

  // Offline persistence — stacks on top of Hocuspocus
  new IndexeddbPersistence(`flow:${flowId}`, ydoc);

  const provider = new HocuspocusProvider({
    url: process.env.NEXT_PUBLIC_COLLAB_WS!, // ws://localhost:4000
    name: `flow:${flowId}`,
    document: ydoc,
    token: supabaseToken, // sent to server's onAuthenticate hook

    onAuthenticationFailed: () => {
      console.error("Collab auth failed — token may have expired");
      // Re-fetch token from Supabase and reconnect
    },
  });

  // Durable canvas state
  const nodesMap = ydoc.getMap<Node>("nodes");
  const edgesMap = ydoc.getMap<Edge>("edges");
  const paramsMap = ydoc.getMap<Record<string, unknown>>("params");

  // Ephemeral awareness: cursors + selections
  const awareness = provider.awareness;
  awareness.setLocalState({
    userId: null, // set after mount with actual user ID
    userName: "",
    color: hashToColor(flowId),
    cursor: null as { x: number; y: number } | null,
    selectedNodes: [] as string[],
  });

  return { ydoc, provider, nodesMap, edgesMap, paramsMap, awareness };
}
```

The `y-indexeddb` provider stacks transparently on top of `HocuspocusProvider`. Students can edit offline; Hocuspocus automatically merges the CRDT updates on reconnect — no manual conflict resolution needed.

### Collaborative objects in the Yjs document

```typescript
const nodesMap = ydoc.getMap<Node>("nodes"); // node_id → Node object
const edgesMap = ydoc.getMap<Edge>("edges"); // edge_id → Edge object
const paramsMap = ydoc.getMap<Params>("params"); // node_id → params dict
// Comments are NOT in Yjs — they live in Supabase (node_comments table)
// and are delivered via Supabase Realtime INSERT events.
```

### Teacher–student collaboration workflow

1. Teacher creates a template flow → marks `is_template = true` → sets `locked_params`
2. Student forks → new Supabase `flows` row (own `owner_id`) + empty `yjs_state`
3. Teacher shares a link: `/pipeline/{flow_id}?collab=1`
4. Both open the canvas. Both connect to `ws://collab:4000` with their respective Supabase JWTs. Hocuspocus's `onAuthenticate` verifies each JWT; `onConnect` checks the flow's `is_public` flag.
5. Teacher cursor appears on student's canvas via Yjs Awareness (ephemeral, not persisted)
6. Teacher right-clicks a node → "Leave comment" → `POST /api/flows/{id}/comments` → inserted into `node_comments` (Supabase)
7. Supabase Realtime fires `INSERT` event on the student's browser channel → yellow badge appears on that node
8. Student resolves comment → `PATCH /api/flows/{id}/comments/{comment_id}` → `resolved = true`

### collab-server dependencies

```json
// collab-server/package.json
{
  "dependencies": {
    "@hocuspocus/server": "^2.0.0",
    "@hocuspocus/extension-database": "^2.0.0",
    "@hocuspocus/extension-logger": "^2.0.0",
    "@supabase/supabase-js": "^2.0.0"
  }
}
```

### Frontend collab dependencies (add to dyslearnia-front)

```json
{
  "@hocuspocus/provider": "^2.0.0",
  "yjs": "^13.6.0",
  "y-indexeddb": "^9.0.0"
}
```

Note: `y-websocket` npm package is **not** needed on the frontend when using `HocuspocusProvider` — Hocuspocus ships its own provider that is protocol-compatible.

---

## 9. Voice Pipeline Builder

### Processing chain

```
Browser MediaRecorder (2s chunks, WAV)
  → WS /ws/speech/stream
  → faster-whisper "tiny" model (local, 39MB)
  → Transcript text
  → Qwen2.5-3B intent parser (strict JSON output)
  → Canvas action dispatcher (frontend)
  → Web Speech API confirmation (browser TTS)
```

### Intent schema (LLM must return one of these)

```json
{ "action": "add_block",      "block_type": string, "position": "start|end|after:{name}" }
{ "action": "connect_blocks", "from": string, "to": string }
{ "action": "remove_block",   "block_name": string }
{ "action": "set_param",      "block_name": string, "param": string, "value": any }
{ "action": "run_pipeline" }
{ "action": "save_flow",      "name": string }
{ "action": "load_template",  "name": string }
{ "action": "unknown",        "raw": string }
```

### Fuzzy block name matching

`"the summarizer"` → strip `"the "` → case-insensitive `includes()` match against `node.data.displayName` in the Zustand store.

### Voice accessibility mode

When `?voice=true` is in the URL, the canvas enters **voice-primary mode**:

- Block palette collapses
- Large waveform visualization takes center stage
- Every action is announced via Web Speech API
- Designed for students with motor disabilities who cannot use mouse/touch

---

## 10. Flow Persistence (Supabase)

### Save/load API

```
POST   /api/flows          — upsert (create or update, idempotent on flow.id)
GET    /api/flows           — list owned + templates
GET    /api/flows/{id}      — load single flow
POST   /api/flows/{id}/fork — fork (copies graph, sets forked_from)
DELETE /api/flows/{id}      — soft delete
PATCH  /api/flows/{id}/promote — teacher: set is_template=true (role check)
```

### Auto-save

Frontend debounces Zustand state changes by 2 seconds. On every debounce flush, a `canvas thumbnail` (via `html2canvas` on the React Flow viewport) and the current graph JSON are `POST`-ed to `/api/flows`. The user never presses Save.

### Template parameterization

A teacher can lock specific params per node before promoting a template:

```json
"locked_params": {
  "n3": ["font"],       // dyslexia_font.font is locked
  "n2": []              // summarizer.ratio is student-configurable
}
```

On fork, locked params render as static labels; unlocked params render as sliders/selects.

---

## 11. Docker Compose — Full Stack

```yaml
# docker-compose.yml
version: "3.9"
services:
  # ── AI / Model layer ─────────────────────────────────────
  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama_data:/root/.ollama
    ports:
      - "11434:11434"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 10s
      retries: 5
    # First run: docker exec dyslearnia-ollama-1 ollama pull qwen2.5:3b

  # ── Graph database ────────────────────────────────────────
  # NOTE: No local Qdrant container — Qdrant Cloud is used (cloud.qdrant.io)
  neo4j:
    image: neo4j:5
    environment:
      NEO4J_AUTH: neo4j/dyslearnia
      NEO4J_PLUGINS: '["apoc"]'
    volumes:
      - neo4j_data:/data
    ports:
      - "7474:7474" # Neo4j Browser (great for demo — judges can explore graph)
      - "7687:7687" # Bolt protocol

  # ── Backend ──────────────────────────────────────────────
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    depends_on:
      ollama:
        condition: service_healthy
      neo4j:
        condition: service_started
    environment:
      OLLAMA_URL: http://ollama:11434
      NEO4J_URI: bolt://neo4j:7687
      NEO4J_USER: neo4j
      NEO4J_PASSWORD: dyslearnia
      QDRANT_URL: ${QDRANT_URL}
      QDRANT_API_KEY: ${QDRANT_API_KEY}
      SUPABASE_URL: ${SUPABASE_URL}
      SUPABASE_SERVICE_KEY: ${SUPABASE_SERVICE_KEY}
    volumes:
      - ./backend:/app
      - model_cache:/app/models

  # ── Collaboration server (Hocuspocus) ─────────────────────
  collab:
    build:
      context: ./collab-server
      dockerfile: Dockerfile
    ports:
      - "4000:4000"
    environment:
      SUPABASE_URL: ${SUPABASE_URL}
      SUPABASE_SERVICE_KEY: ${SUPABASE_SERVICE_KEY}
      PORT: 4000

  # ── Frontend ──────────────────────────────────────────────
  frontend:
    build:
      context: ./dyslearnia-front
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    depends_on:
      - backend
      - collab
    environment:
      NEXT_PUBLIC_API_URL: http://backend:8000
      NEXT_PUBLIC_COLLAB_WS: ws://collab:4000
      NEXT_PUBLIC_SUPABASE_URL: ${SUPABASE_URL}
      NEXT_PUBLIC_SUPABASE_ANON_KEY: ${SUPABASE_ANON_KEY}

volumes:
  ollama_data:
  neo4j_data:
  model_cache:
```

### Dockerfiles

**backend/Dockerfile**

```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y \
    ffmpeg libsndfile1 \
    # WeasyPrint dependencies
    libpango-1.0-0 libpangoft2-1.0-0 libcairo2 libgdk-pixbuf2.0-0 \
    # LibreOffice headless — for PPTX → PNG slide thumbnails
    libreoffice --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

**collab-server/Dockerfile**

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package.json .
RUN npm install
COPY . .
RUN npm run build
CMD ["node", "dist/server.js"]
```

**dyslearnia-front/Dockerfile**

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json .
RUN npm install
COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json .
RUN npm install --production
CMD ["npm", "start"]
```

---

## 12. Environment Variables

```bash
# .env.example — copy to .env and fill in

# Supabase (get from supabase.com → project settings → API)
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJ...          # server-side only, never expose to browser
SUPABASE_ANON_KEY=eyJ...             # browser-safe public key

# Qdrant Cloud (get from cloud.qdrant.io → cluster → API keys)
QDRANT_URL=https://xxxx.qdrant.io:6333
QDRANT_API_KEY=your-qdrant-api-key

# Neo4j (internal Docker network)
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=dyslearnia

# Ollama (internal Docker network)
OLLAMA_URL=http://ollama:11434

# Frontend (override for local dev — use localhost, not container names)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_COLLAB_WS=ws://localhost:4000
NEXT_PUBLIC_SUPABASE_URL=https://xxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
```

---

## 13. Existing Agent → IBlock Migration Map

The existing `backend/agents/` files are not discarded — they are **wrapped** as IBlock implementations. This preserves working code while plugging it into the pipeline architecture.

| Existing agent          | Becomes                                                                     | Wrapping strategy                                                            |
| ----------------------- | --------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| `orchestrator.py`       | `engine/runner.py`                                                          | Refactor into PipelineRunner class; keep routing logic                       |
| `text_simplifier.py`    | `blocks/transform/summarizer.py`                                            | Wrap `simplify()` in `IBlock.execute()`, add RAGMixin                        |
| `quiz_agent.py`         | `blocks/transform/quiz_builder.py`                                          | Wrap quiz generation, add `source_chunks` to output                          |
| `hint_agent.py`         | `blocks/transform/gap_detector.py`                                          | Wrap hint logic, write gaps to `student_progress` Supabase table             |
| `gamification_agent.py` | `blocks/transform/gamification.py`                                          | Wrap XP logic, write to `student_progress.xp`                                |
| `audio_agent.py`        | `blocks/inputs/course_input.py` (video path) + `blocks/output/tts_block.py` | Transcription logic → CourseInputBlock video extractor; synthesis → TTSBlock |
| `ocr_agent.py`          | `blocks/inputs/course_input.py` (PDF path)                                  | OCR/text extraction → CourseInputBlock PDF extractor                         |
| `models/local_llm.py`   | unchanged                                                                   | All blocks import `ollama_generate()` from here                              |
| `utils/audio.py`        | unchanged                                                                   | TTSBlock and AudioUnifierBlock import from here                              |
| `utils/embeddings.py`   | replaced by `db/qdrant.py`                                                  | Qdrant Cloud client replaces local embedding store                           |
| `utils/speech_input.py` | `routes/speech.py`                                                          | Expose as FastAPI WebSocket route                                            |

---

## 14. Demo Script (Hackathon Pitch)

**Total time: 3 minutes**

### Segment 1 — Problem (30 sec)

> "Every student in this room gets the same PDF. But Ahmed has dyslexia. Sana learns visually. Omar is cramming for tomorrow's exam. They all need something completely different. DysLearnia lets each of them build the pipeline that works for their brain."

### Segment 2 — Live demo (90 sec)

**Pipeline 1 — Dyslexia (20 sec):**  
Upload a real lecture PDF → drag `Summarizer (40%)` → drag `Dyslexia Font` → drag `TTS` → hit Run → show the OpenDyslexic-rendered page + audio player

**Pipeline 2 — Visual learner (20 sec):**  
Same PDF already uploaded → drag `Key Concepts` → drag `Knowledge Graph` → hit Run → show interactive D3 force graph, open Neo4j Browser sidebar showing the same graph as Cypher nodes

**Pipeline 3 — Exam prep (20 sec):**  
Drag `Flashcards` → drag `Quiz` → drag `Gap Detector` → hit Run → show flashcard deck → show quiz with score → show gap detector output: "You are weak on: Osmosis, Active Transport"

**Collaboration (30 sec):**  
Open a second browser window as "Dr. Hamza (Teacher)" → join the student's pipeline → move teacher cursor → right-click a node → leave comment "Try reducing compression to 30% for this dense topic" → show comment badge appearing on student's screen in real time

### Segment 3 — Architecture (30 sec)

> "Every block is a modular component. The pipeline engine chains them. Qdrant Cloud keeps every AI output grounded in the source document — you can see the citations right here. Everything runs locally on a 3-billion-parameter model. No OpenAI. No Gemini. Fully compliant."

### Segment 4 — Impact (30 sec)

> "This isn't a chatbot that answers questions. It's a learning content factory that every student configures for their own brain. The same course material, but processed their way."

---

## 15. Key Technical Decisions & Rationale

| Decision                         | Alternative considered                                | Why this choice                                                                                                                                            |
| -------------------------------- | ----------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Qwen2.5-3B via Ollama            | Llama 3.2-3B, Phi-3-mini                              | Qwen2.5 is strongest multilingual instruct model under 5B; Arabic support matters for SMU context                                                          |
| React Flow (@xyflow/react)       | Custom SVG canvas, D3 force                           | React Flow is production-proven, used by n8n itself; built-in node/edge types, zoom, minimap                                                               |
| Hocuspocus over raw y-websocket  | y-websocket server, PartyKit                          | Hocuspocus adds auth hooks, Database extension, and per-document access control out of the box; y-websocket requires all of this to be built manually      |
| Yjs CRDT                         | Firebase Realtime, Supabase Realtime for canvas state | Yjs is correct by construction — no central merge logic, offline-first; Supabase Realtime is used only for comments (which need persistence, not CRDT)     |
| Qdrant Cloud only (no ChromaDB)  | ChromaDB local + Qdrant local                         | One service, one API, handles both per-doc RAG and cross-doc search via payload filters. Eliminates a container, simplifies setup, free tier is sufficient |
| Supabase for persistence         | Raw PostgreSQL, PlanetScale                           | Auth already integrated in existing codebase (`lib/supabase/`); Storage for file uploads; Realtime for comment notifications                               |
| Neo4j for knowledge graphs       | NetworkX + JSON, ArangoDB                             | Cypher prerequisite-chain traversal in one query; Neo4j Browser is a free visual demo tool judges can explore live                                         |
| WeasyPrint for PDF unifier       | ReportLab, Playwright headless                        | WeasyPrint accepts HTML+CSS → PDF natively; markdown → HTML via `python-markdown` is trivial; images embed as base64; no browser binary needed             |
| python-pptx for PPTX unifier     | LibreOffice headless export                           | python-pptx has direct Python API for slides, text, images; no subprocess or office suite required at runtime                                              |
| MoviePy v2 for video unifier     | ffmpeg subprocess, Manim                              | MoviePy v2 has clean Python API for `ImageClip` + `AudioFileClip` concat; no raw ffmpeg command assembly; ships `libx264` via imageio-ffmpeg               |
| pydub for audio unifier          | ffmpeg subprocess, soundfile                          | pydub handles concat, normalization, and MP3 export in pure Python; pairs naturally with Kokoro WAV output                                                 |
| faster-whisper "tiny" for speech | Whisper "base", cloud API                             | Tiny is 39MB, transcribes in under 1 second on CPU; "base" adds latency with no meaningful accuracy gain for command intent parsing                        |
| Kokoro-82M for TTS               | espeak, gTTS (cloud)                                  | Kokoro produces natural speech entirely locally; 82M params, runs on CPU in real time                                                                      |

---

## 16. Requirements

### backend/requirements.txt (extend existing)

```
fastapi
uvicorn[standard]
python-multipart
websockets
# AI / models
ollama
faster-whisper
kokoro                    # local TTS (Kokoro-82M)
sentence-transformers     # all-MiniLM-L6-v2 for embeddings
# Vector / Graph
qdrant-client             # Qdrant Cloud SDK
neo4j                     # Neo4j async driver
# Document processing — course_input block
pymupdf                   # PDF text extraction + page-to-PNG render (fitz)
python-pptx               # PPTX text extraction + slide building (unifier)
pillow                    # image manipulation for infographic block
python-markdown           # markdown → HTML for PDF unifier
weasyprint                # HTML → PDF rendering
pydub                     # audio concat + normalization (audio unifier)
moviepy                   # video assembly (video unifier) — install v2: pip install moviepy>=2.0
# Utilities
python-dotenv
supabase
```

### collab-server/package.json

```json
{
  "name": "dyslearnia-collab",
  "scripts": {
    "build": "tsc",
    "start": "node dist/server.js",
    "dev": "ts-node server.ts"
  },
  "dependencies": {
    "@hocuspocus/server": "^2.13.0",
    "@hocuspocus/extension-database": "^2.13.0",
    "@hocuspocus/extension-logger": "^2.13.0",
    "@supabase/supabase-js": "^2.0.0",
    "yjs": "^13.6.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "ts-node": "^10.0.0",
    "@types/node": "^20.0.0"
  }
}
```

### dyslearnia-front/package.json (add to existing)

```json
{
  "dependencies": {
    "@xyflow/react": "^12.0.0",
    "@hocuspocus/provider": "^2.13.0",
    "yjs": "^13.6.0",
    "y-indexeddb": "^9.0.0",
    "zustand": "^4.0.0",
    "use-debounce": "^10.0.0",
    "html2canvas": "^1.4.0"
  }
}
```

Note: `y-websocket` is **not** needed on the frontend — `@hocuspocus/provider` is the client-side provider and is protocol-compatible with the Hocuspocus server.

---

## 17. First-Sprint Checklist

Minimum to have a working demo for the hackathon:

- [ ] `IBlock` base class + `BlockData` dataclass
- [ ] `@register_block` decorator + registry endpoint `GET /api/blocks`
- [ ] `CourseInputBlock` — PDF path first (PyMuPDF), then PPTX, then video
- [ ] Migrate `text_simplifier.py` → `SummarizerBlock` with RAGMixin (first LLM block, proves the pattern)
- [ ] `PipelineRunner` topological executor
- [ ] FastAPI WebSocket `/ws/pipeline/{run_id}` with progress events
- [ ] Qdrant Cloud collection setup + `index_document()` called on upload
- [ ] React Flow canvas with `BlockNode` custom node + `BlockPalette` sidebar
- [ ] Zustand store wired to WebSocket events (node status: idle → running → done)
- [ ] Supabase `flows` table + `yjs_state` column + auto-save
- [ ] Hocuspocus server with `onAuthenticate` (Supabase JWT) + Database extension
- [ ] `HocuspocusProvider` on frontend + `CollaboratorCursors` component
- [ ] `DyslexiaFontBlock` (pure HTML reformatter, no LLM — quick win)
- [ ] `KnowledgeGraphBlock` → Neo4j write → D3 force graph render
- [ ] **PDF unifier** (WeasyPrint): markdown text + infographic PNGs → downloadable PDF
- [ ] **PPTX unifier** (python-pptx): text sections + PNGs → downloadable .pptx
- [ ] **Audio unifier** (Kokoro + pydub): text sections → merged MP3
- [ ] **Video unifier** (MoviePy v2): slide PNGs + WAV audio → MP4
- [ ] Three preset templates loadable from template gallery
- [ ] Voice builder (Whisper + intent LLM + dispatcher)
- [ ] `docker compose up` boots everything cleanly (Ollama + Neo4j + backend + collab + frontend)

---

_This document is the single source of truth for the DysLearnia system. All implementation decisions should trace back to a section here. When in doubt, refer to Section 2 (hackathon alignment) — every feature must serve at least one judging criterion._
