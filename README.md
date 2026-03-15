<div align="center">

<br/>

<!-- LOGO / HERO -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://readme-typing-svg.demolab.com?font=Space+Mono&weight=700&size=42&duration=0&pause=1000&color=A78BFA&center=true&vCenter=true&width=600&height=80&lines=DysLearnia" />
  <source media="(prefers-color-scheme: light)" srcset="https://readme-typing-svg.demolab.com?font=Space+Mono&weight=700&size=42&duration=0&pause=1000&color=6D28D9&center=true&vCenter=true&width=600&height=80&lines=DysLearnia" />
  <img src="https://readme-typing-svg.demolab.com?font=Space+Mono&weight=700&size=42&duration=0&pause=1000&color=A78BFA&center=true&vCenter=true&width=600&height=80&lines=DysLearnia" alt="DysLearnia" />
</picture>

<br/>

<p>
  <em>Your course material, processed your way.</em>
</p>

<p>
  <strong>AI-powered learning pipeline builder &mdash; drag, chain, transform, export.</strong><br/>
  Built for the SMU Hackathon 5th Edition &bull; Theme: Education in the Era of AI
</p>

<br/>

<!-- BADGE ROW 1 — stack -->
<p>
  <img src="https://img.shields.io/badge/Next.js-14-000000?style=for-the-badge&logo=nextdotjs&logoColor=white" alt="Next.js 14"/>
  <img src="https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Ollama-Qwen2.5--3B-F97316?style=for-the-badge&logo=ollama&logoColor=white" alt="Ollama"/>
  <img src="https://img.shields.io/badge/Supabase-Auth%20%2B%20DB-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white" alt="Supabase"/>
</p>

<!-- BADGE ROW 2 — infra -->
<p>
  <img src="https://img.shields.io/badge/Qdrant-Cloud-DC2626?style=for-the-badge&logo=qdrant&logoColor=white" alt="Qdrant Cloud"/>
  <img src="https://img.shields.io/badge/Neo4j-Knowledge%20Graph-4581C3?style=for-the-badge&logo=neo4j&logoColor=white" alt="Neo4j"/>
  <img src="https://img.shields.io/badge/Hocuspocus-Collab-8B5CF6?style=for-the-badge&logo=y-combinator&logoColor=white" alt="Hocuspocus"/>
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker"/>
</p>

<!-- BADGE ROW 3 — meta -->
<p>
  <img src="https://img.shields.io/badge/Model-≤%205B%20params-10B981?style=for-the-badge" alt="Model ≤5B"/>
  <img src="https://img.shields.io/badge/External%20APIs-Zero-EF4444?style=for-the-badge" alt="Zero external APIs"/>
  <img src="https://img.shields.io/badge/License-MIT-94A3B8?style=for-the-badge" alt="MIT"/>
  <img src="https://img.shields.io/badge/Status-Hackathon%20Build-F59E0B?style=for-the-badge" alt="Hackathon"/>
</p>

<br/>

---

</div>

<!-- PIPELINE DEMO STRIP -->
<div align="center">

```
  ╔══════════════╗     ╔═══════════════╗     ╔══════════════╗     ╔═══════════════╗     ╔══════════════╗
  ║ 📄 COURSE   ║────▶║ ✂  SUMMARIZE ║────▶║ 🧠 KNOWLEDGE ║────▶║ 🎤 TTS AUDIO  ║────▶║ 📦 EXPORT   ║
  ║   INPUT     ║     ║   (40% ratio) ║     ║    GRAPH     ║     ║  (Kokoro-82M) ║     ║    UNIFIER  ║
  ║ PDF·PPTX·MP4║     ║   RAG-grounded║     ║ Neo4j+D3.js  ║     ║  local · fast ║     ║ PDF·PPTX·MP4║
  ╚══════════════╝     ╚═══════════════╝     ╚══════════════╝     ╚═══════════════╝     ╚══════════════╝
```

**Every block is a modular AI component. Chain them to build your own learning experience.**

</div>

---

## 📖 Table of Contents

- [What is DysLearnia?](#-what-is-dyslearnia)
- [The Pipeline Concept](#-the-pipeline-concept)
- [Block Library](#-block-library)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Data Layer](#-data-layer)
- [Real-time Collaboration](#-real-time-collaboration)
- [Voice Pipeline Builder](#-voice-pipeline-builder)
- [Output Unifiers](#-output-unifiers)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [Project Structure](#-project-structure)
- [Preset Pipelines](#-preset-pipelines)
- [Hackathon Alignment](#-hackathon-alignment)
- [Contributing](#-contributing)

---

## 🧠 What is DysLearnia?

DysLearnia is **not a chatbot**. It is a visual learning content factory.

Every student receives the same lecture PDF. But a student with dyslexia needs large-spaced OpenDyslexic text and audio narration. A visual learner needs an interactive knowledge graph. An exam-prepper needs flashcards, a quiz, and a gap analysis report. None of them need the same thing — yet every LMS serves them identical static content.

DysLearnia solves this with a **drag-and-drop pipeline builder** inspired by n8n. Students chain processing blocks — each one an AI task — to transform their course materials into the format that works for _their_ brain. The pipeline is the product.

> _"Not a chatbot. A learning content factory that every student configures for their own brain."_

### Why it wins all three challenge tracks at once

| Challenge Track                         | DysLearnia's Answer                                                                           |
| --------------------------------------- | --------------------------------------------------------------------------------------------- |
| **Adaptive Learning & Personalization** | Per-student saved flows, gap detector, quiz performance tracking, Qdrant RAG grounding        |
| **Inclusive Learning for Disabilities** | Dyslexia font block, TTS, simplified text, voice-driven canvas for motor disabilities         |
| **Course-Specific AI Tutoring**         | RAG tutor chat block grounded in uploaded documents — cites source chunks, never hallucinates |

---

## ⛓️ The Pipeline Concept

The entire system is modelled on one idea: **a typed data envelope (`BlockData`) flows between composable blocks**.

```python
@dataclass
class BlockData:
    text:          str   | None   # markdown, plain text
    binary:        bytes | None   # audio (wav), image (png), video (mp4), pdf
    mime_type:     str   | None   # "audio/wav" | "image/png" | "video/mp4" | ...
    metadata:      dict           # word_count, confidence, reading_level, ...
    source_chunks: list[str]      # Qdrant RAG excerpts — surfaced as citations in UI
```

Every block implements one interface:

```python
class IBlock(ABC):
    @abstractmethod
    async def execute(self, inputs: list[BlockData], params: dict) -> list[BlockData]:
        ...
```

The `PipelineRunner` topologically sorts the canvas DAG and calls `execute()` on each block in dependency order, streaming live WebSocket progress events back to the canvas.

---

## 🧩 Block Library

### Input

| Block            | Formats                             | What it does                                                                                                                                                                    |
| ---------------- | ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Course input** | `.pdf` `.pptx` `.mp4` `.mov` `.mkv` | Auto-detects format. PDF → PyMuPDF. PPTX → python-pptx + LibreOffice thumbnails. Video → faster-whisper transcript + keyframes. Indexes all chunks into Qdrant Cloud on upload. |

### Transform

| Block               | Input               | Output       | Key params                                   |
| ------------------- | ------------------- | ------------ | -------------------------------------------- |
| **Summarizer**      | text                | text         | ratio 10–90%, style (bullets/paragraph/tldr) |
| **Key concepts**    | text                | text         | max concepts 5–30                            |
| **Knowledge graph** | text                | graph + text | depth 1–3, min confidence                    |
| **Flashcard gen**   | text                | text         | count 5–50, difficulty                       |
| **Quiz builder**    | text                | text         | count, MCQ/short/true-false                  |
| **Gap detector**    | text + quiz results | text         | threshold                                    |
| **Simplified text** | text                | text         | CEFR level A1–C2                             |
| **Dyslexia font**   | text                | HTML         | OpenDyslexic/Lexie, spacing, line-height     |
| **Infographic**     | text                | PNG          | theme, columns                               |
| **TTS**             | text                | WAV          | speed 0.5–2.0×, voice preset                 |
| **Tutor chat**      | text                | interactive  | terminal block — opens grounded chat         |
| **Gamification**    | quiz results        | text         | XP multiplier                                |

### Output Unifiers ✨

| Block             | Accepts                          | Produces | Tooling                                                    |
| ----------------- | -------------------------------- | -------- | ---------------------------------------------------------- |
| **PDF unifier**   | markdown text + infographic PNGs | `.pdf`   | `python-markdown` → HTML → **WeasyPrint**                  |
| **PPTX unifier**  | text sections + PNGs             | `.pptx`  | **python-pptx** — one slide per H2 heading                 |
| **Video unifier** | slide PNGs + WAV audio           | `.mp4`   | **MoviePy v2** `ImageClip` + `AudioFileClip` → libx264/aac |
| **Audio unifier** | text sections + WAV clips        | `.mp3`   | **Kokoro-82M** synthesis + **pydub** concat/normalize      |

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│  Next.js 14  ·  React Flow (@xyflow/react)  ·  Zustand + Yjs        │
│  HocuspocusProvider  ·  Voice (MediaRecorder)  ·  Flow Library       │
└──────────────┬─────────────────────────────────────┬─────────────────┘
               │  REST  /  WebSocket                 │  WS room per flow
               ▼                                     ▼
┌─────────────────────────┐             ┌─────────────────────────────┐
│  FastAPI  :8000         │             │  Hocuspocus  :4000          │
│  ├ Block registry       │             │  ├ onAuthenticate (JWT)      │
│  ├ Pipeline runner      │             │  ├ onConnect (RLS check)     │
│  ├ Flow CRUD            │             │  └ Database extension        │
│  └ Speech intent WS     │             │    (Supabase yjs_state)      │
└──────┬──────────────────┘             └─────────────────────────────┘
       │
       ├──▶  Ollama :11434  (Qwen2.5-3B  ·  ≤5B params  ·  fully local)
       ├──▶  faster-whisper (tiny, 39MB  ·  transcription + voice commands)
       ├──▶  Kokoro-82M     (local TTS   ·  WAV → audio unifier)
       ├──▶  PyMuPDF  /  python-pptx  /  LibreOffice headless
       ├──▶  WeasyPrint  /  MoviePy v2  /  pydub
       └──▶  D3.js (knowledge graph rendering, served as JSON)

┌──────────────────────────────────────────────────────────────────────┐
│  Data Layer                                                          │
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────────┐ │
│  │ Supabase        │  │ Qdrant Cloud     │  │ Neo4j  :7474/:7687  │ │
│  │ Auth + flows    │  │ course_chunks    │  │ Concept nodes       │ │
│  │ progress + RLS  │  │ RAG + cross-doc  │  │ RELATION edges      │ │
│  │ Storage (files) │  │ 384-dim cosine   │  │ APOC + Browser UI   │ │
│  │ Realtime (cmts) │  │ filter by doc_id │  │ Cypher prereq chains│ │
│  └─────────────────┘  └──────────────────┘  └─────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

<table>
<tr>
<th>Layer</th>
<th>Technology</th>
<th>Why</th>
</tr>
<tr>
<td><strong>Frontend</strong></td>
<td>Next.js 14 (App Router) + TypeScript</td>
<td>Existing codebase, server components, file-based routing</td>
</tr>
<tr>
<td><strong>Canvas</strong></td>
<td><code>@xyflow/react</code> (React Flow)</td>
<td>Production-proven pipeline canvas — the same library powering n8n</td>
</tr>
<tr>
<td><strong>State</strong></td>
<td>Zustand + Yjs CRDT</td>
<td>Local state in Zustand; collaborative canvas state in Yjs Y.Map</td>
</tr>
<tr>
<td><strong>Collaboration</strong></td>
<td>Hocuspocus + y-indexeddb</td>
<td>Auth hooks, DB persistence extension, offline CRDT sync</td>
</tr>
<tr>
<td><strong>Backend</strong></td>
<td>FastAPI + Python 3.11</td>
<td>Async, typed, existing codebase</td>
</tr>
<tr>
<td><strong>LLM</strong></td>
<td>Qwen2.5-3B-Instruct via Ollama</td>
<td>Best multilingual model ≤5B; Arabic support; instruction-tuned</td>
</tr>
<tr>
<td><strong>Transcription</strong></td>
<td>faster-whisper (tiny, 39MB)</td>
<td>Sub-second CPU transcription; used for video input AND voice commands</td>
</tr>
<tr>
<td><strong>TTS</strong></td>
<td>Kokoro-82M</td>
<td>Natural-sounding local speech synthesis; no cloud dependency</td>
</tr>
<tr>
<td><strong>Embeddings</strong></td>
<td>sentence-transformers all-MiniLM-L6-v2</td>
<td>22MB, 384-dim, fast on CPU; feeds Qdrant Cloud</td>
</tr>
<tr>
<td><strong>PDF export</strong></td>
<td>python-markdown + WeasyPrint</td>
<td>Markdown → HTML → print-quality PDF; images as base64; no browser binary</td>
</tr>
<tr>
<td><strong>PPTX export</strong></td>
<td>python-pptx</td>
<td>Direct Python API; text sections → slides; PNGs as full-bleed image slides</td>
</tr>
<tr>
<td><strong>Video export</strong></td>
<td>MoviePy v2</td>
<td>ImageClip + AudioFileClip → libx264/aac MP4; clean Python API</td>
</tr>
<tr>
<td><strong>Audio export</strong></td>
<td>pydub</td>
<td>Concat WAV clips, normalize, export MP3; pairs with Kokoro output</td>
</tr>
<tr>
<td><strong>PPTX input</strong></td>
<td>python-pptx + LibreOffice headless</td>
<td>Text extraction + slide thumbnails in Docker</td>
</tr>
<tr>
<td><strong>PDF input</strong></td>
<td>PyMuPDF (fitz)</td>
<td>Fast text extraction + page-to-PNG rendering</td>
</tr>
</table>

---

## 🗄️ Data Layer

### Supabase — auth, flows, progress, comments, file storage

```sql
-- Saved pipelines (the core entity)
flows            (id, owner_id, title, graph jsonb, is_template, locked_params, yjs_state, ...)

-- Per-node teacher comments
node_comments    (id, flow_id, node_id, author_role, body, resolved)

-- Student performance tracking
student_progress (user_id, xp, streak_days, knowledge_gaps jsonb)

-- Pipeline run cache (avoid reprocessing unchanged upstream nodes)
pipeline_runs    (id, flow_id, user_id, run_data jsonb, completed_at)
```

Row-level security: students see only their own flows + any `is_template = true` or `is_public = true` flows. Supabase Realtime broadcasts comment inserts to the student's browser channel instantly.

### Qdrant Cloud — single vector store for everything

One `course_chunks` collection handles **both** use cases via payload filters:

```
Per-document RAG:    filter doc_id = "uuid"     → grounded LLM prompts
Cross-doc search:    filter user_id = "uuid"    → tutor chat, gap detector
```

No local vector database container. Free tier (1GB) is sufficient for a hackathon.

### Neo4j — knowledge graph

Concepts are `(:Concept {name, doc_id})` nodes connected by `[:RELATION {type}]` edges. The `knowledge_graph` block extracts `(subject, relation, object)` triples via the LLM and writes them with `MERGE`. The `tutor_chat` block queries prerequisite chains with Cypher.

**Neo4j Browser** (`:7474`) is exposed in the Docker stack — judges can explore the live knowledge graph interactively during the demo.

---

## 👥 Real-time Collaboration

Built on **Yjs CRDT** + **Hocuspocus** (not raw y-websocket — Hocuspocus adds the auth and persistence that y-websocket lacks out of the box).

```
Student opens /pipeline/[id]
    │
    ├─ HocuspocusProvider connects to ws://collab:4000
    │    └─ sends Supabase access_token as auth token
    │
    ├─ Hocuspocus onAuthenticate: verifies JWT with Supabase
    ├─ Hocuspocus onConnect: checks flows.owner_id or is_public
    │
    ├─ Database extension fetches yjs_state from Supabase → hydrates Y.Doc
    │
    ├─ y-indexeddb stacks on top → offline edits sync on reconnect
    │
    └─ Yjs Awareness: teacher cursor + selected nodes → ephemeral, not persisted
```

Teacher comments are **not** in Yjs — they live in `node_comments` (Supabase) and arrive via Supabase Realtime `INSERT` events, so they persist across sessions.

```
Teacher right-clicks node → POST /api/flows/{id}/comments
    └─ Supabase Realtime fires INSERT → student's browser
           └─ yellow badge appears on that node immediately
```

---

## 🎤 Voice Pipeline Builder

Students with motor disabilities, or anyone who thinks faster than they can drag blocks, can build an entire pipeline by speaking.

```
Hold-to-talk button  →  MediaRecorder streams 2s WAV chunks
    └─ WS /ws/speech/stream
           └─ faster-whisper "tiny"  →  transcript
                  └─ Qwen2.5-3B intent parser  →  strict JSON action
                         └─ Canvas dispatcher
                                └─ Web Speech API confirmation (spoken)
```

**Supported commands:**

```
"Add a summarizer block"
"Connect the summarizer to the text to speech"
"Set compression to 30 percent"
"Remove the quiz block"
"Run the pipeline"
"Save this as my chemistry notes flow"
```

Voice-primary mode (`?voice=true`): block palette collapses, waveform visualizer takes center stage. Designed for students who cannot use mouse or touch input.

---

## 📦 Output Unifiers

The four unifier blocks sit at the end of any pipeline and produce a **real downloadable file** from everything upstream.

### PDF Unifier

```
markdown text(s) + infographic PNG(s)
    └─ python-markdown  →  HTML body
    └─ base64-embed PNGs as <figure> tags
    └─ WeasyPrint CSS  →  print-quality PDF
         themes: clean | dyslexia (OpenDyslexic, 2× line-height) | dark
```

### PPTX Unifier

```
text sections + image PNGs
    └─ python-pptx:
         title slide  ←  first text block
         content slides  ←  split on ## headings, 16pt bullets
         image slides  ←  one full-bleed PNG per infographic
    └─  .pptx  →  Supabase Storage  →  download link
```

### Video Unifier

```
slide PNGs + WAV audio (from TTS block)
    └─ MoviePy v2:
         ImageClip per PNG  ×  N seconds each
         optional TextClip captions from paired text blocks
         AudioFileClip  ←  WAV narration
         concatenate_videoclips  →  libx264 / aac
    └─  .mp4  →  download
```

### Audio Unifier

```
text sections + WAV clips
    └─ for raw text  →  Kokoro-82M synthesis  →  WAV
    └─ pydub:
         concat all segments + silence padding
         normalize loudness
         export MP3 128k
    └─  .mp3  →  download
```

---

## 🚀 Getting Started

### Prerequisites

- Docker + Docker Compose
- A [Supabase](https://supabase.com) project (free)
- A [Qdrant Cloud](https://cloud.qdrant.io) cluster (free tier)

### 1. Clone and configure

```bash
git clone https://github.com/your-org/dyslearnia.git
cd dyslearnia
cp .env.example .env
# Fill in SUPABASE_URL, SUPABASE_SERVICE_KEY, SUPABASE_ANON_KEY,
# QDRANT_URL, QDRANT_API_KEY
```

### 2. Start the full stack

```bash
docker compose up --build
```

This starts: **Ollama** (model server) · **Neo4j** · **FastAPI backend** · **Hocuspocus collab server** · **Next.js frontend**

### 3. Pull the LLM

```bash
docker exec dyslearnia-ollama-1 ollama pull qwen2.5:3b
```

### 4. Run Supabase migrations

```bash
# Apply the SQL schema from PROMPT.md Section 7.1 in your Supabase SQL editor
# or use the Supabase CLI:
supabase db push
```

### 5. Open

```
Frontend:      http://localhost:3000
Backend API:   http://localhost:8000/docs
Neo4j Browser: http://localhost:7474   (neo4j / dyslearnia)
```

---

## ⚙️ Environment Variables

```bash
# ── Supabase ──────────────────────────────────────────────
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJ...      # server-side only
SUPABASE_ANON_KEY=eyJ...         # browser-safe

# ── Qdrant Cloud ──────────────────────────────────────────
QDRANT_URL=https://xxxx.qdrant.io:6333
QDRANT_API_KEY=your-qdrant-api-key

# ── Neo4j (Docker internal) ───────────────────────────────
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=dyslearnia

# ── Ollama (Docker internal) ──────────────────────────────
OLLAMA_URL=http://ollama:11434

# ── Frontend public vars ──────────────────────────────────
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_COLLAB_WS=ws://localhost:4000
NEXT_PUBLIC_SUPABASE_URL=https://xxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
```

---

## 📁 Project Structure

```
dyslearnia/
├── docker-compose.yml
├── .env.example
│
├── backend/                         FastAPI app
│   ├── blocks/
│   │   ├── base.py                  IBlock ABC + BlockData
│   │   ├── registry.py              @register_block decorator
│   │   ├── inputs/
│   │   │   └── course_input.py      ← PDF · PPTX · Video (auto-detect)
│   │   ├── transform/
│   │   │   ├── summarizer.py        RAGMixin + Qwen2.5
│   │   │   ├── knowledge_graph.py   LLM triples → Neo4j → D3
│   │   │   ├── quiz_builder.py
│   │   │   ├── gap_detector.py
│   │   │   └── ...
│   │   └── output/
│   │       ├── tts_block.py         Kokoro-82M
│   │       ├── dyslexia_block.py    HTML reformatter
│   │       ├── infographic.py       Pillow + Jinja2 → PNG
│   │       └── unifiers/
│   │           ├── pdf_unifier.py   WeasyPrint
│   │           ├── pptx_unifier.py  python-pptx
│   │           ├── video_unifier.py MoviePy v2
│   │           └── audio_unifier.py pydub
│   ├── engine/
│   │   ├── runner.py                Topological executor + WS events
│   │   └── validator.py             Edge type compatibility
│   ├── mixins/
│   │   └── rag_mixin.py             Qdrant Cloud retrieval + grounding
│   └── db/
│       ├── qdrant.py                Cloud client + index/retrieve/search
│       ├── neo4j.py                 Async driver + upsert/neighborhood
│       └── supabase.py              Client singleton
│
├── collab-server/                   Hocuspocus Node.js server
│   └── server.ts                    Auth · Database extension · Supabase
│
└── dyslearnia-front/                Next.js 14 app
    └── app/
        ├── components/
        │   ├── canvas/              React Flow + BlockNode + BlockPalette
        │   ├── collaboration/       CollaboratorCursors + CommentThread
        │   ├── speech/              VoiceButton + dispatcher
        │   └── library/             FlowLibrary + TemplateGallery
        ├── store/
        │   └── pipeline.ts          Zustand + HocuspocusProvider
        └── pipeline/[id]/           Pipeline editor route
```

---

## 🎯 Preset Pipelines

Three one-click templates ship with DysLearnia:

<table>
<tr>
<th>Template</th>
<th>Pipeline</th>
<th>For</th>
</tr>
<tr>
<td>🔤 <strong>Dyslexia-Friendly Notes</strong></td>
<td><code>Course Input</code> → <code>Summarizer 40%</code> → <code>Dyslexia Font</code> → <code>TTS</code> → <code>Audio Unifier</code></td>
<td>Students with dyslexia, visual stress, reading difficulties</td>
</tr>
<tr>
<td>🕸️ <strong>Visual Knowledge Map</strong></td>
<td><code>Course Input</code> → <code>Key Concepts</code> → <code>Knowledge Graph</code> → <code>Infographic</code> → <code>PDF Unifier</code></td>
<td>Visual learners, concept mapping, exam revision</td>
</tr>
<tr>
<td>📝 <strong>Exam Sprint</strong></td>
<td><code>Course Input</code> → <code>Summarizer 30%</code> → <code>Flashcards</code> → <code>Quiz</code> → <code>Gap Detector</code></td>
<td>Students cramming before exams, knowledge gap identification</td>
</tr>
</table>

Teachers can promote any custom flow as a template, lock specific parameters, and share it with a class.

---

## 🏆 Hackathon Alignment

### Judging criteria scorecard

| Criterion                              | Weight | Our answer                                                                                              |
| -------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------- |
| **Innovation & Original Thinking**     | 15%    | Visual pipeline metaphor for learning — no other team will bring this abstraction                       |
| **AI Integration & Educational Value** | 15%    | Every block is an AI task; outputs compound across the pipeline; tutor chat is RAG-grounded             |
| **System Architecture & Engineering**  | 10%    | `IBlock` interface, `@register_block` registry, topological `PipelineRunner` — textbook modularity      |
| **Reliability & Grounded Responses**   | 10%    | Qdrant RAG on every LLM block; `source_chunks` shown as citations; `_confidence_score()` hedge detector |
| **Model Compliance**                   | 5%     | Qwen2.5-3B via Ollama — fully local, 3B ≪ 5B limit, zero external API calls anywhere                    |
| **Usability & Learning Experience**    | 10%    | Drag-and-drop canvas, preset templates, voice builder, real-time collaboration with teachers            |
| **Presentation & Demo**                | 15%    | Three live pipelines in 90 seconds; teacher/student collab live; Neo4j Browser graph walkthrough        |

### The 3-minute pitch

> **"Every student gets the same PDF. But no two students learn the same way."**
>
> 30s — Problem  
> 90s — Three live pipelines (dyslexia · knowledge graph · exam prep)  
> 30s — Architecture (one diagram, one sentence per layer)  
> 30s — Impact: _"The same course material, processed your way."_

---

## 🤝 Contributing

This project was built for SMU Hackathon 5th Edition. The architecture is designed to be extended — adding a new block requires a single Python file with `@register_block` and the frontend auto-discovers it via `GET /api/blocks`.

```python
# Example: add a MindMap block in 30 lines
@register_block
class MindMapBlock(IBlock, RAGMixin):
    description = BlockDescription(
        name="mind_map",
        display_name="Mind map",
        group="transform",
        input_types=["text"],
        output_types=["binary/svg"],
        parameters=[{"name": "depth", "type": "slider", "min": 1, "max": 4, "default": 2}]
    )

    async def execute(self, inputs, params):
        chunks = self._retrieve(inputs[0].text[:200], inputs[0].metadata["doc_id"])
        # ... generate SVG ...
        return [BlockData(binary=svg_bytes, mime_type="image/svg+xml")]
```

---

<div align="center">

<br/>

Built with ♥ for the **SMU Hackathon 5th Edition**

<img src="https://img.shields.io/badge/Made%20with-Python%20%2B%20TypeScript-3776AB?style=flat-square&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/AI-100%25%20Local-10B981?style=flat-square"/>
<img src="https://img.shields.io/badge/External%20APIs-0-EF4444?style=flat-square"/>

<br/><br/>

_"Not a chatbot. A learning content factory."_

</div>
